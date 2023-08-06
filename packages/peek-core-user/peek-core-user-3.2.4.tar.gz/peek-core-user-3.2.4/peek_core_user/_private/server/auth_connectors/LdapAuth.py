import hashlib
import logging
from typing import List
from typing import Tuple

from peek_core_user._private.PluginNames import userPluginTuplePrefix

from peek_core_user._private.server.auth_connectors.AuthABC import AuthABC

from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.LdapSetting import LdapSetting
from peek_core_user._private.storage.Setting import (
    globalSetting,
    LDAP_VERIFY_SSL,
)
from peek_core_user.tuples.constants.UserAuthTargetEnum import (
    UserAuthTargetEnum,
)

from twisted.cred.error import LoginFailed

__author__ = "synerty"

logger = logging.getLogger(__name__)

import ldap

"""
{'objectClass': [b'top', b'person', b'organizationalPerson', b'user'], 'cn': [b'attest'],
 'givenName': [b'attest'],
 'distinguishedName': [b'CN=attest,OU=testou,DC=synad,DC=synerty,DC=com'],
 'instanceType': [b'4'], 'whenCreated': [b'20170505160836.0Z'],
 'whenChanged': [b'20190606130621.0Z'], 'displayName': [b'attest'],
 'uSNCreated': [b'16498'],
 'memberOf': [b'CN=Domain Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Enterprise Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Administrators,CN=Builtin,DC=synad,DC=synerty,DC=com'],
 'uSNChanged': [b'73784'], 'name': [b'attest'],
 'objectGUID': [b'\xee\x1bV\x8dQ\xackE\x82\xd9%_\x18\xadjO'],
 'userAccountControl': [b'66048'], 'badPwdCount': [b'0'], 'codePage': [b'0'],
 'countryCode': [b'0'], 'badPasswordTime': [b'132042996316396717'], 'lastLogoff': [b'0'],
 'lastLogon': [b'132042996806397639'], 'pwdLastSet': [b'132042997225927009'],
 'primaryGroupID': [b'513'], 'objectSid': [
    b'\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00D:3|X\x8f\xc7\x08\xe6\xeaV\xc8Q\x04\x00\x00'],
 'adminCount': [b'1'], 'accountExpires': [b'9223372036854775807'], 'logonCount': [b'36'],
 'sAMAccountName': [b'attest'], 'sAMAccountType': [b'805306368'],
 'userPrincipalName': [b'attest@synad.synerty.com'], 'lockoutTime': [b'0'],
 'objectCategory': [b'CN=Person,CN=Schema,CN=Configuration,DC=synad,DC=synerty,DC=com'],
 'dSCorePropagationData': [b'20190606130621.0Z', b'20190606130016.0Z',
                           b'20170506090346.0Z', b'16010101000000.0Z'],
 'lastLogonTimestamp': [b'132042996806397639']}
"""


class LdapNotEnabledError(Exception):
    pass


class LdapAuth(AuthABC):
    def checkPassBlocking(
        self, dbSession, userName, password, forService, userUuid=None
    ):
        """Login User

        :param forService:
        :param dbSession:
        :param userName: The username of the user.
        :param password: The users secret password.
        :param userUuid: The decoded objectSid of the user from LDAP
        :rtype
        """

        assert forService in (1, 2, 3), "Unhandled for service type"

        ldapSettings: List[LdapSetting] = dbSession.query(LdapSetting).all()

        if not globalSetting(dbSession, LDAP_VERIFY_SSL):
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        if not ldapSettings:
            raise Exception("LDAPAuth: No LDAP servers configured.")

        firstException = None

        for ldapSetting in ldapSettings:
            if forService == self.FOR_ADMIN:
                if not ldapSetting.adminEnabled:
                    continue

            elif forService == self.FOR_OFFICE:
                if not ldapSetting.desktopEnabled:
                    continue

            elif forService == self.FOR_FIELD:
                if not ldapSetting.mobileEnabled:
                    continue

            else:
                raise Exception(
                    "LDAPAuth: Unhandled forService type %s" % forService
                )

            if (
                "@" in userName
                and userName.split("@")[1] != ldapSetting.ldapDomain
            ):
                continue

            try:
                return self._tryLdap(
                    dbSession, userName, password, ldapSetting, userUuid
                )
            except LoginFailed as e:
                if not firstException:
                    firstException = e

        logger.error("Login failed for %s, %s", userName, str(firstException))

        if firstException:
            raise firstException

        raise LoginFailed("LDAPAuth: No LDAP providers found for this service")

    def _tryLdap(
        self,
        dbSession,
        userName,
        password,
        ldapSetting: LdapSetting,
        userUuid=None,
    ) -> Tuple[List[str], InternalUserTuple]:
        try:

            conn = ldap.initialize(ldapSetting.ldapUri)
            conn.protocol_version = 3
            conn.set_option(ldap.OPT_REFERRALS, 0)

            # make the connection
            conn.simple_bind_s(
                "%s@%s" % (userName.split("@")[0], ldapSetting.ldapDomain),
                password,
            )
            if userUuid:
                ldapFilter = (
                    "(&(objectCategory=person)(objectClass=user)(objectSid=%s))"
                    % userUuid
                )
            else:
                ldapFilter = (
                    "(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))"
                    % userName.split("@")[0]
                )

            dcParts = ",".join(
                ["DC=%s" % part for part in ldapSetting.ldapDomain.split(".")]
            )

            ldapBases = []
            if ldapSetting.ldapOUFolders:
                ldapBases += self._makeLdapBase(
                    ldapSetting.ldapOUFolders, userName, "OU"
                )
            if ldapSetting.ldapCNFolders:
                ldapBases += self._makeLdapBase(
                    ldapSetting.ldapCNFolders, userName, "CN"
                )

            if not ldapBases:
                raise LoginFailed(
                    "LDAPAuth: LDAP OU and/or CN search paths must be set."
                )

            userDetails = None
            for ldapBase in ldapBases:
                ldapBase = "%s,%s" % (ldapBase, dcParts)

                try:
                    # Example Base : 'CN=atuser1,CN=Users,DC=synad,DC=synerty,DC=com'
                    userDetails = conn.search_st(
                        ldapBase, ldap.SCOPE_SUBTREE, ldapFilter, None, 0, 10
                    )

                    if userDetails:
                        break

                except ldap.NO_SUCH_OBJECT:
                    logger.warning("CN or OU doesn't exist : %s", ldapBase)

        except ldap.NO_SUCH_OBJECT:
            raise LoginFailed(
                "LDAPAuth: An internal error occurred, ask admin to check "
                "Attune logs"
            )

        except ldap.INVALID_CREDENTIALS:
            raise LoginFailed("LDAPAuth: Username or password is incorrect")

        if not userDetails:
            raise LoginFailed(
                "LDAPAuth: User doesn't belong to the correct CN/OUs"
            )

        userDetails = userDetails[0][1]

        distinguishedName = userDetails.get("distinguishedName")[0].decode()
        primaryGroupId = userDetails.get("primaryGroupID")[0].decode()
        objectSid = userDetails.get("objectSid")[0]
        # python-ldap doesn't include key `memberOf` in search result
        #  if the user doesn't belong to any groups.
        memberOfSet = set(userDetails.get("memberOf", []))

        decodedSid = LdapAuth._decodeSid(objectSid)
        primaryGroupSid = (
            "-".join(decodedSid.split("-")[:-1]) + "-" + primaryGroupId
        )

        ldapFilter = "(objectSid=%s)" % primaryGroupSid
        primGroupDetails = conn.search_st(
            dcParts, ldap.SCOPE_SUBTREE, ldapFilter, None, 0, 10
        )
        memberOfSet.add(primGroupDetails[0][1].get("distinguishedName")[0])

        # find all it's groups and groups of those groups
        # The magic number in this filter allows us to fetch the groups of
        # a group.
        ldapFilter = (
            "(&(objectCategory=group)(member:1.2.840.113556.1.4.1941:=%s))"
            % (LdapAuth._escapeParensForLdapFilter(distinguishedName),)
        )
        groupDetails = conn.search_st(
            ",".join(distinguishedName.split(",")[1:]),
            ldap.SCOPE_SUBTREE,
            ldapFilter,
            None,
            0,
            10,
        )

        if groupDetails:
            for group in groupDetails:
                groupMemberOf = group[1].get("memberOf", [])
                memberOfSet.update(groupMemberOf)

        groups = []
        for memberOf in memberOfSet:
            group = memberOf.decode().split(",")[0]
            if "=" in group:
                group = group.split("=")[1]
            groups.append(group)

        userTitle = None
        if userDetails["displayName"]:
            userTitle = userDetails["displayName"][0].decode()

        email = None
        if userDetails["userPrincipalName"]:
            email = userDetails["userPrincipalName"][0].decode()

        if not userUuid:
            userUuid = LdapAuth._decodeSid(objectSid)

        if ldapSetting.ldapGroups:
            ldapGroups = set(
                [s.strip() for s in ldapSetting.ldapGroups.split(",")]
            )

            if not ldapGroups & set(groups):
                raise LoginFailed("User is not a member of an authorised group")

        newInternalUser = self._maybeCreateInternalUserBlocking(
            dbSession,
            userName,
            userTitle,
            userUuid,
            email,
            ldapSetting.ldapTitle,
            objectSid,
        )

        return groups, newInternalUser

    def _decodeSid(sid: [bytes]) -> str:
        strSid = "S-"
        sid = iter(sid)

        # Byte 0 is the revision
        revision = next(sid)
        strSid += "%s" % (revision,)

        # Byte 1 is the count of sub-authorities
        countSubAuths = next(sid)

        # Byte 2-7 (big endian) form the 48-bit authority code
        bytes27 = [next(sid) for _ in range(2, 8)]
        authority = int.from_bytes(bytes27, byteorder="big")
        strSid += "-%s" % (authority,)

        for _ in range(countSubAuths):
            # Each is 4 bytes (32-bits) in little endian
            subAuthBytes = [next(sid) for _ in range(4)]
            subAuth = int.from_bytes(subAuthBytes, byteorder="little")
            strSid += "-%s" % (subAuth,)

        return strSid

    def _escapeParensForLdapFilter(value: str) -> str:
        """Escape parenthesis () in a string

        Escape special characters in a string to be able to use it as a value
        in an LDAP filter. `(` are replaced with \28 and `)` are replaced
        with \29 and so on.

        Reference: https://tools.ietf.org/search/rfc2254#page-5

        :return: Escaped string
        """
        # The \ character must always be escaped first
        value = value.replace("\\", "\\5C")

        value = value.replace("(", "\\28")
        value = value.replace(")", "\\29")
        value = value.replace("*", "\\2A")
        value = value.replace("\0", "\\00")
        return value

    def _maybeCreateInternalUserBlocking(
        self,
        dbSession,
        userName,
        userTitle,
        userUuid,
        email,
        ldapName,
        objectSid,
    ) -> InternalUserTuple:

        internalUser = (
            dbSession.query(InternalUserTuple)
            .filter(InternalUserTuple.userUuid == userUuid)
            .first()
        )

        # do no create, return the existing user
        if internalUser:
            if "@" not in internalUser.userKey:
                internalUser.userKey = (
                    internalUser.userName
                    if "@" in internalUser.userName
                    else (
                        "%s@%s"
                        % (
                            internalUser.userName,
                            internalUser.email.split("@")[1],
                        )
                    )
                )
                dbSession.merge(internalUser)
                dbSession.commit()

            return internalUser

        newInternalUser = InternalUserTuple(
            userName=userName,
            userKey=(
                userName
                if "@" in userName
                else ("%s@%s" % (userName, email.split("@")[1]))
            ),
            userTitle="%s (%s)" % (userTitle, ldapName),
            userUuid=userUuid,
            email=email,
            authenticationTarget=UserAuthTargetEnum.LDAP,
            importSource="LDAP",
            # importHash e.g. 'peek_core_user.LDAPAuth:<md5 hash>'
            importHash=f"{userPluginTuplePrefix}{self.__class__.__name__}:{userUuid}",
        )

        try:
            dbSession.add(newInternalUser)
        except Exception as e:
            logger.info(e)
            raise LoginFailed(
                "Failed to create Internal User. Use the full name <username>@<ldap-domain> to login"
            )
        dbSession.commit()
        return newInternalUser

    def _makeLdapBase(self, ldapFolders, userName, propertyName):
        try:
            ldapBases = []
            for folder in ldapFolders.split(","):
                folder = folder.strip()
                if not folder:
                    continue

                parts = []
                for part in folder.split("/"):
                    part = part.strip()
                    if not part:
                        continue
                    parts.append("%s=%s" % (propertyName, part))

                ldapBases.append(",".join(reversed(parts)))

            return ldapBases

        except Exception as e:
            logger.error(
                "Login failed for %s, failed to parse LDAP %s Folders setting",
                propertyName,
                userName,
            )

            logger.exception(e)

            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs"
            )
