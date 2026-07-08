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
        assert len(tiers) == 8
        password_tiers = [
            t for t in tiers if t.get("product_type") not in ("watch", "creative")
        ]
        assert len(password_tiers) == 4
        assert all(t["price"] > 0 for t in tiers)

    def test_creative_categories(self, api):
        r = requests.get(f"{api}/api/creative/categories")
        assert r.status_code == 200
        categories = r.json()
        assert len(categories) == 4
        assert any(c["id"] == "funny" and c["optional_seeds"] for c in categories)


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

    def test_checkout_passphrase_mode(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "svinomat", "email": unique_email, "mode": "passphrase"},
        )
        assert r.status_code == 200, r.text
        order_id = r.json()["order_id"]
        body = requests.get(f"{api}/api/orders/{order_id}/result").json()
        assert "-" in body["password"]
        assert body["entropy_bits"] > 40

    def test_checkout_backup_codes(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "backup", "email": unique_email},
        )
        assert r.status_code == 200, r.text
        order_id = r.json()["order_id"]
        body = requests.get(f"{api}/api/orders/{order_id}/result").json()
        assert body.get("product_type") == "backup_codes"
        assert len(body.get("backup_codes", [])) == 10

    def test_checkout_creative_klichki(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={
                "tier": "klichki",
                "email": unique_email,
                "category": "funny",
                "seed_words": ["bacon"],
            },
        )
        assert r.status_code == 200, r.text
        order_id = r.json()["order_id"]
        assert "/names/success" in r.json()["confirmation_url"]
        body = requests.get(f"{api}/api/orders/{order_id}/result").json()
        assert body.get("product_type") == "creative"
        assert body.get("creative_kind") == "nicknames"
        assert len(body.get("creative_items", [])) == 15
        assert body.get("creative_category") == "funny"

    def test_checkout_creative_requires_category(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "socpak", "email": unique_email},
        )
        assert r.status_code == 400

    def test_checkout_creative_socpak(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={
                "tier": "socpak",
                "email": unique_email,
                "category": "funny",
                "seed_words": ["мем"],
            },
        )
        assert r.status_code == 200, r.text
        order_id = r.json()["order_id"]
        body = requests.get(f"{api}/api/orders/{order_id}/result").json()
        assert body.get("creative_kind") == "social"
        assert len(body.get("creative_items", [])) == 10
        assert len(body.get("creative_bios", [])) == 3

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
    def test_fulfill_backup_codes(self, db_session, unique_email):
        from app.repositories import order_repo
        from app.services.ephemeral import pop_fulfillment
        from app.services.fulfillment import fulfill_order
        from app.services.payment import create_paid_order

        order = create_paid_order(db_session, unique_email, "backup")
        order_repo.mark_paid(db_session, order)
        fulfill_order(db_session, order.id)
        payload = pop_fulfillment(str(order.id))
        assert payload is not None
        assert payload["product_type"] == "backup_codes"
        assert len(payload["backup_codes"]) == 10

    def test_fulfill_creative(self, db_session, unique_email):
        from app.repositories import order_repo
        from app.services.ephemeral import pop_fulfillment
        from app.services.fulfillment import fulfill_order
        from app.services.payment import create_paid_order

        order = create_paid_order(
            db_session,
            unique_email,
            "klichki",
            order_options={"category": "funny", "seed_words": ["bacon"]},
        )
        order_repo.mark_paid(db_session, order)
        fulfill_order(db_session, order.id)
        payload = pop_fulfillment(str(order.id))
        assert payload is not None
        assert payload["product_type"] == "creative"
        assert len(payload["creative_items"]) == 15
        assert payload["creative_category"] == "funny"

    def test_order_report_not_legend(self, api, unique_email):
        r = requests.post(
            f"{api}/api/checkout",
            json={"tier": "svinomat", "email": unique_email},
        )
        order_id = r.json()["order_id"]
        report = requests.get(f"{api}/api/orders/{order_id}/report")
        assert report.status_code == 404

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
