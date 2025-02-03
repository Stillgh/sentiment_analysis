import hashlib
import uuid

from app.src.entities.user.user_role import UserRole


class User:
    def __init__(self, id: uuid, name: str, surname: str, login: str, password: str, balance: float, role: UserRole):
        self.__id = id
        self.__name = name
        self.__surname = surname
        self.__login = login
        self.__hashed_password = self.__hash_password(password)
        self.__balance = balance
        self.__role = role

    def __hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    # Getters
    @property
    def id(self) -> uuid:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def surname(self) -> str:
        return self.__surname

    @property
    def login(self) -> str:
        return self.__login

    @property
    def balance(self) -> float:
        return self.__balance

    @property
    def role(self) -> UserRole:
        return self.__role

    # Setters
    @name.setter
    def name(self, value: str):
        self.__name = value

    @surname.setter
    def surname(self, value: str):
        self.__surname = value

    @login.setter
    def login(self, value: str):
        self.__login = value

    @balance.setter
    def balance(self, value: float):
        self.__balance = value

    @role.setter
    def role(self, value: UserRole):
        self.__role = value

