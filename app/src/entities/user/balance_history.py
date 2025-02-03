import datetime
import uuid


class BalanceHistory:
    def __init__(self, user_id: uuid, amount_before_change: float, amount_change: float, timestamp: datetime):
        self.__user_id = user_id
        self.__amount_before_change = amount_before_change
        self.__amount_change = amount_change
        self.__timestamp = timestamp

    @property
    def user_id(self) -> uuid:
        return self.__user_id

    @user_id.setter
    def user_id(self, value: uuid):
        self.__user_id = value

    @property
    def amount_before_change(self) -> float:
        return self.__amount_before_change

    @amount_before_change.setter
    def amount_before_change(self, value: float):
        self.__amount_before_change = value

    @property
    def amount_change(self) -> float:
        return self.__amount_change

    @amount_change.setter
    def amount_change(self, value: float):
        self.__amount_change = value

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, value: datetime):
        self.__timestamp = value
