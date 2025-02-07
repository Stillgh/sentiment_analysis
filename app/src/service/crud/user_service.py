import uuid
from typing import List
import bcrypt
from entities.user.user import User
from sqlmodel import Session, select
from fastapi import HTTPException
from entities.user.user_role import UserRole

from entities.user.balance_history import BalanceHistory


def get_all_users(session: Session) -> List[User]:
    return session.query(User).all()


def get_user_by_id(id: uuid.UUID, session: Session) -> List[User]:
    return session.get(User, id)


def get_user_by_email(email: str, session: Session) -> User:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user


def create_user(new_user: User, session: Session) -> None:
    session.add(new_user)
    session.commit()
    session.refresh(new_user)


def add_balance(email: str, amount: float, session: Session) -> None:
    if amount <= 0:
        raise Exception("Amount must be positive")

    user = get_user_by_email(email, session)
    if not user:
        raise Exception("User not found")

    balance_history = BalanceHistory(user_id=user.id, amount_before_change=user.balance, amount_change=amount)

    user.balance += amount
    session.add(balance_history)
    session.commit()
    session.refresh(user)


def withdraw_balance(email: str, amount: float, session: Session) -> None:
    if amount <= 0:
        raise Exception("Amount must be positive")

    user = get_user_by_email(email, session)
    if not user:
        raise Exception("User not found")

    if user.balance < amount:
        raise Exception("Insufficient balance")

    balance_history = BalanceHistory(user_id=user.id, amount_before_change=user.balance, amount_change=-amount)

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


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_admin_user(session: Session) -> None:
    admin_email = "admin@example.com"  # You might want to get this from settings
    
    admin = get_user_by_email(admin_email, session)
    if admin:
        return
    
    admin = User(
        id=uuid.uuid4(),
        email=admin_email,
        name="Admin",
        surname="Admin",
        hashed_password=hash_password("admin123"),
        balance=100_000_000.0,
        role=UserRole.ADMIN
    )
    
    try:
        create_user(admin, session)
        print("Admin user created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        raise HTTPException(status_code=500, detail="Could not create admin user")


