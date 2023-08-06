import logging

from peek_core_user._private.server.auth_connectors.AuthABC import AuthABC
from peek_core_user._private.server.auth_connectors.LdapAuth import LdapAuth
from peek_core_user._private.server.controller.PasswordUpdateController import (
    PasswordUpdateController,
)
from peek_core_user._private.storage.InternalGroupTuple import (
    InternalGroupTuple,
)
from peek_core_user._private.storage.InternalUserGroupTuple import (
    InternalUserGroupTuple,
)
from peek_core_user._private.storage.InternalUserPassword import (
    InternalUserPassword,
)
from peek_core_user.tuples.constants.UserAuthTargetEnum import (
    UserAuthTargetEnum,
)
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.Setting import (
    globalSetting,
    ADMIN_LOGIN_GROUP,
    OFFICE_LOGIN_GROUP,
    MOBILE_LOGIN_GROUP,
)
from peek_core_user.server.UserDbErrors import (
    UserPasswordNotSetException,
    UserNotFoundException,
)
from twisted.cred.error import LoginFailed

logger = logging.getLogger(__name__)


class InternalAuth(AuthABC):
    def checkPassBlocking(self, dbSession, userName, password, forService):

        authenticatedUser = (
            dbSession.query(InternalUserTuple, InternalUserPassword)
            .join(InternalUserPassword, isouter=True)  # effectively `LEFT JOIN`
            .filter(InternalUserTuple.userName == userName)
            .first()
        )

        # if user not found
        if not authenticatedUser or not authenticatedUser.InternalUserTuple:
            raise UserNotFoundException(userName)

        # if user found but user is created by LDAP
        if (
            authenticatedUser.InternalUserTuple.authenticationTarget
            == UserAuthTargetEnum.LDAP
        ):
            # delegate to LDAPAuth
            return LdapAuth().checkPassBlocking(
                dbSession, userName, password, forService
            )

        if not authenticatedUser.InternalUserPassword:
            raise UserPasswordNotSetException(userName)

        passObj = authenticatedUser.InternalUserPassword
        if passObj.password != PasswordUpdateController.hashPass(password):
            raise LoginFailed(
                "Peek InternalAuth: Username or password is incorrect"
            )

        groups = (
            dbSession.query(InternalGroupTuple)
            .join(InternalUserGroupTuple)
            .filter(InternalUserGroupTuple.userId == passObj.userId)
            .all()
        )

        groupNames = [g.groupName for g in groups]

        if forService == self.FOR_ADMIN:
            adminGroup = globalSetting(dbSession, ADMIN_LOGIN_GROUP)
            if adminGroup not in set(groupNames):
                raise LoginFailed(
                    "Peek InternalAuth: User is not apart of an authorised group"
                )

        elif forService == self.FOR_OFFICE:
            officeGroup = globalSetting(dbSession, OFFICE_LOGIN_GROUP)
            if officeGroup not in set(groupNames):
                raise LoginFailed(
                    "Peek InternalAuth: User is not apart of an authorised group"
                )

        elif forService == self.FOR_FIELD:
            fieldGroup = globalSetting(dbSession, MOBILE_LOGIN_GROUP)
            if fieldGroup not in set(groupNames):
                raise LoginFailed(
                    "Peek InternalAuth: User is not apart of an authorised group"
                )

        else:
            raise Exception(
                "Peek InternalAuth: Unhandled forService type %s" % forService
            )

        return groupNames, authenticatedUser.InternalUserTuple
