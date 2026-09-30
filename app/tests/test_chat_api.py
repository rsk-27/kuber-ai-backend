from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models import User
from app.tests.conftest import TestingSessionLocal


client = TestClient(app)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_chat_purchase():
    db = TestingSessionLocal()

    try:
        user = User(name="Chat Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        response = client.post(
            "/chat",
            json={
                "user_id": user.id,
                "message": "I want to invest ₹500 in gold",
                "idempotency_key": "chat-purchase-test-001"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["user_id"] == user.id
        assert data["intent"] == "PURCHASE"
        assert "Purchase completed successfully" in data["response"]

    finally:
        db.close()


def test_chat_rejects_zero_purchase_amount():
    db = TestingSessionLocal()

    try:
        user = User(name="Invalid Purchase User")
        db.add(user)
        db.commit()
        db.refresh(user)

        response = client.post(
            "/chat",
            json={
                "user_id": user.id,
                "message": "I want to invest ₹0 in gold",
                "idempotency_key": "chat-zero-purchase-001"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["intent"] == "PURCHASE"
        assert "greater than zero" in data["response"]

    finally:
        db.close()



def test_chat_creates_sip():
    db = TestingSessionLocal()

    try:
        user = User(name="SIP Chat User")
        db.add(user)
        db.commit()
        db.refresh(user)

        response = client.post(
            "/chat",
            json={
                "user_id": user.id,
                "message": "Create a monthly SIP of ₹1000",
                "idempotency_key": "chat-sip-test-001"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["user_id"] == user.id
        assert data["intent"] == "SIP"
        assert "SIP created successfully" in data["response"]
        assert "₹1000" in data["response"]
        assert "MONTHLY" in data["response"]

    finally:
        db.close()


def test_chat_rejects_negative_purchase_amount():
    db = TestingSessionLocal()
    try:
        user = User(name="Negative Purchase User")
        db.add(user)
        db.commit()
        db.refresh(user)

        response = client.post(
            "/chat",
            json={
                "user_id": user.id,
                "message": "Buy gold worth -5000",
                "idempotency_key": "chat-negative-purchase-001"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["intent"] == "PURCHASE"
        assert "greater than zero" in data["response"]

    finally:
        db.close()