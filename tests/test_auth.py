from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.core.security import hash_password, verify_password
from app.db.models import Order, RefundRequest, User


def test_password_hashing():
    hashed = hash_password("Correct-Horse-123!")
    assert hashed != "Correct-Horse-123!"
    assert verify_password("Correct-Horse-123!", hashed)
    assert not verify_password("wrong-password", hashed)


def test_register_login_me_and_authenticated_order_chat():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            register = client.post("/api/v1/auth/register", json={"email": "tester@example.com", "password": "TestPass123!"})
            assert register.status_code == 201, register.text
            token = register.json()["access_token"]
            assert register.json()["user"]["email"] == "tester@example.com"

            # Seed an order owned by the newly registered user for authenticated flow tests.
            db = TestingSessionLocal()
            test_user = db.query(User).filter_by(email="tester@example.com").first()
            db.add(Order(order_number="SA-TEST-100", user_id=test_user.id, product_name="Test headphones", status="shipped", amount=1999.0))
            db.commit()
            db.close()

            anonymous_order = client.post("/api/v1/chat", json={"message": "Where is my order?"})
            assert anonymous_order.status_code == 200
            assert "sign in" in anonymous_order.json()["response"].lower()

            authed_order = client.post("/api/v1/chat", json={"message": "Where is my order?"}, headers={"Authorization": f"Bearer {token}"})
            assert authed_order.status_code == 200, authed_order.text
            assert "SA-TEST-100" in authed_order.json()["response"]

            refund = client.post("/api/v1/chat", json={"message": "I want a refund for my order."}, headers={"Authorization": f"Bearer {token}"})
            assert refund.status_code == 200, refund.text
            db = TestingSessionLocal()
            assert db.query(RefundRequest).count() == 1
            db.close()

            me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert me.status_code == 200
            assert me.json()["email"] == "tester@example.com"

            duplicate = client.post("/api/v1/auth/register", json={"email": "tester@example.com", "password": "AnotherPass123!"})
            assert duplicate.status_code == 409

            login = client.post("/api/v1/auth/login", json={"email": "tester@example.com", "password": "TestPass123!"})
            assert login.status_code == 200, login.text
            assert "access_token" in login.json()

            bad_login = client.post("/api/v1/auth/login", json={"email": "tester@example.com", "password": "wrong"})
            assert bad_login.status_code == 422 or bad_login.status_code == 401
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
