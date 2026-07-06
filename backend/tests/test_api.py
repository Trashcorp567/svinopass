import re
import uuid

import requests


class TestPublicAPI:
    def test_health(self, api):
        r = requests.get(f"{api}/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_tiers_paid_only(self, api):
        r = requests.get(f"{api}/api/tiers")
        assert r.status_code == 200
        tiers = r.json()
        assert len(tiers) == 3
        assert all(t["price"] > 0 for t in tiers)


class TestCheckout:
    def test_checkout_mock_fulfill(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "svinomat", "email": unique_email},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        order_id = data["order_id"]
        assert "confirmation_url" in data

        result = requests.get(f"{api}/api/orders/{order_id}/result")
        assert result.status_code == 200, result.text
        body = result.json()
        assert len(body["password"]) == 20
        assert body["entropy_bits"] > 50
        assert body["email_sent"] is True

    def test_result_one_time_only(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "bacon", "email": unique_email},
        )
        order_id = r.json()["order_id"]
        assert requests.get(f"{api}/api/orders/{order_id}/result").status_code == 200
        assert requests.get(f"{api}/api/orders/{order_id}/result").status_code == 410

    def test_checkout_bacon_symbols(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "bacon", "email": unique_email},
        )
        order_id = r.json()["order_id"]
        pwd = requests.get(f"{api}/api/orders/{order_id}/result").json()["password"]
        assert len(pwd) == 24
        assert re.search(r"[a-z]", pwd)
        assert re.search(r"[A-Z]", pwd)
        assert re.search(r"\d", pwd)
        assert re.search(r"[!@#$%^&*\-_=+?]", pwd)

    def test_unknown_tier(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "khryak", "email": unique_email},
        )
        assert r.status_code == 400

    def test_invalid_email(self, api):
        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "svinomat", "email": "not-an-email"},
        )
        assert r.status_code == 422

    def test_password_not_stored_in_db(self, api, unique_email, db_session):
        from uuid import UUID

        from app.db.models import Order

        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "svinomat", "email": unique_email},
        )
        order_id = r.json()["order_id"]
        order = db_session.query(Order).filter(Order.id == UUID(order_id)).first()
        assert order is not None
        assert order.status == "paid"
        assert order.fulfilled_at is not None
        assert "password" not in Order.__table__.columns


class TestWebhook:
    def test_fulfill_idempotent(self, db_session, unique_email):
        from app.repositories import order_repo
        from app.services.fulfillment import fulfill_order
        from app.services.payment import create_paid_order

        order = create_paid_order(db_session, unique_email, "svinomat")
        order_repo.mark_paid(db_session, order)
        fulfill_order(db_session, order.id)
        fulfill_order(db_session, order.id)
        db_session.refresh(order)
        assert order.fulfilled_at is not None
