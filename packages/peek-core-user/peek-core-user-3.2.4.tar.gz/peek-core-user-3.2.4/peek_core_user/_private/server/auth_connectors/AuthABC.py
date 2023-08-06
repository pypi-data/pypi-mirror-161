from abc import ABCMeta
from abc import abstractmethod
from typing import List
from typing import Tuple

from sqlalchemy.orm import Session

from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple


class AuthABC(metaclass=ABCMeta):
    FOR_ADMIN = 1
    FOR_OFFICE = 2
    FOR_FIELD = 3

    @abstractmethod
    def checkPassBlocking(
        self, dbSession: Session, userName: str, password: str, forService: int
    ) -> Tuple[List[str], InternalUserTuple]:
        raise NotImplementedError
