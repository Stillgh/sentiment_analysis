import datetime


class PredictionResult:
    def __init__(self, result, __is_success: bool, balance_withdrawal: float, result_timestamp: datetime):
        self.__result = result
        self.__is_success = __is_success
        self.__balance_withdrawal = balance_withdrawal
        self.__result_timestamp = result_timestamp

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, value):
        self.__result = value

    @property
    def is_success(self) -> bool:
        return self.__is_success

    @is_success.setter
    def is_success(self, value: bool):
        self.__is_success = value

    @property
    def balance_withdrawal(self) -> float:
        return self.__balance_withdrawal

    @balance_withdrawal.setter
    def balance_withdrawal(self, value: float):
        self.__balance_withdrawal = value

    @property
    def result_timestamp(self) -> datetime:
        return self.__result_timestamp

    @result_timestamp.setter
    def result_timestamp(self, value: datetime):
        self.__result_timestamp = value
