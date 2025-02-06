from datetime import datetime
import uuid

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sqlmodel import Session

from entities.task.prediction_request import PredictionRequest
from entities.ml_model.classification_model import ClassificationModel
from entities.user.user import User
from entities.user.user_role import UserRole

from service.crud.model_service import create_model, get_all_models, make_prediction, get_all_prediction_history
from service.crud.user_service import create_user, get_all_users, add_balance, withdraw_balance, get_balance_histories
from database.database import init_db, engine
from database.config import get_settings


def test_create_mlmodels():
    logistic_regression_model = LogisticRegression()
    gradient_boosting_model = GradientBoostingClassifier()
    log_reg = ClassificationModel(
        name='LogisticRegression',
        model=logistic_regression_model,
        prediction_cost=100.0
    )

    grad_boost = ClassificationModel(
        name='GradientBoostingClassifier',
        model=gradient_boosting_model,
        prediction_cost=500.0
    )

    with Session(engine) as session:
        create_model(log_reg, session)
        create_model(grad_boost, session)
        models = get_all_models(session)
    for model in models:
        print(model)

    return models


def test_create_users():
    admin = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        name="Admin",
        surname="User",
        hashed_password="testpwd",
        balance=1000.0,
        role=UserRole.ADMIN
    )

    # Create regular users
    user1 = User(
        id=uuid.uuid4(),
        email="john.doe@example.com",
        name="John",
        surname="Doe",
        hashed_password="testpwd",
        balance=500.0,
        role=UserRole.USER
    )

    with Session(engine) as session:
        create_user(admin, session)
        create_user(user1, session)
        users = get_all_users(session)
    for user in users:
        print(f'id: {user.id} - {user.email}')

    return users


def test_add_and_withdraw_balance(balance: float):
    with Session(engine) as session:
        users = get_all_users(session)

        user_1 = users[0]
        print(f'id: {user_1.id} - balance before {user_1.balance}')
        print(f'Adding {balance} credits')
        add_balance(user_1.id, balance, session)
        print(f'id: {user_1.id} - balance after {user_1.balance}')

        user_2 = users[1]
        print(f'id: {user_2.id} - balance before {user_2.balance}')
        print(f'Withdrawing {balance} credits')
        withdraw_balance(user_2.id, balance, session)
        print(f'id: {user_2.id} - balance after {user_2.balance}')


def test_balance_histories(user_id: uuid.UUID):
    with Session(engine) as session:
        balances = get_balance_histories(user_id, session)
        print(f'Balance history for user {user_id}: {balances}')


def test_prediction_tasks(user: User, model: ClassificationModel):
    requests = [
        PredictionRequest(
            user_id=user.id,
            model_id=model.id,
            inference_input="[1, 2, 3, 4]",
            user_balance_before_task=user.balance,
            request_timestamp=datetime.now()
        ),
        PredictionRequest(
            user_id=user.id,
            model_id=model.id,
            inference_input="[5, 6, 7, 8]",
            user_balance_before_task=user.balance,
            request_timestamp=datetime.now()
        )
    ]
    with Session(engine) as session:
        make_prediction(requests, model, session)
        tasks = get_all_prediction_history(session)
        print(f'Prediction tasks history size {len(tasks)} tasks: {tasks}')


if __name__ == "__main__":
    settings = get_settings()
    init_db()
    print("Initiated database")

    users = test_create_users()
    test_add_and_withdraw_balance(50)
    test_add_and_withdraw_balance(200)
    test_balance_histories(users[1].id)

    models = test_create_mlmodels()

    test_prediction_tasks(users[0], models[0])
