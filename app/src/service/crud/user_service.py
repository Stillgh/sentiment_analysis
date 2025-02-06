import uuid
from typing import List

from entities.user.user import User
from sqlmodel import Session, select

from entities.user.balance_history import BalanceHistory


def get_all_users(session: Session) -> List[User]:
    return session.query(User).all()


def get_user_by_id(id: uuid.UUID, session: Session) -> List[User]:
    return session.get(User, id)


def create_user(new_user: User, session: Session) -> None:
    session.add(new_user)
    session.commit()
    session.refresh(new_user)


def add_balance(user_id: uuid.UUID, amount: float, session: Session) -> None:
    if amount <= 0:
        raise Exception("Amount must be positive")

    user = session.get(User, user_id)
    if not user:
        raise Exception("User not found")

    balance_history = BalanceHistory(user_id=user_id, amount_before_change=user.balance, amount_change=amount)

    user.balance += amount
    session.add(balance_history)
    session.commit()
    session.refresh(user)


def withdraw_balance(user_id: uuid.UUID, amount: float, session: Session) -> None:
    if amount <= 0:
        raise Exception("Amount must be positive")

    user = session.get(User, user_id)
    if not user:
        raise Exception("User not found")

    if user.balance < amount:
        raise Exception("Insufficient balance")

    balance_history = BalanceHistory(user_id=user_id, amount_before_change=user.balance, amount_change=-amount)

    user.balance -= amount
    session.add(balance_history)
    session.commit()
    session.refresh(user)


def get_balance_histories(user_id: uuid.UUID, session: Session) -> List[BalanceHistory]:
    statement = select(BalanceHistory) \
        .where(BalanceHistory.user_id == user_id) \
        .order_by(BalanceHistory.timestamp.desc())

    result = session.exec(statement).all()
    return result