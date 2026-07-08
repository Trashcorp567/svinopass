from app.services.breach_client import fetch_email_breaches


def test_fetch_email_breaches_mock_clean(monkeypatch):
    monkeypatch.setattr("app.services.breach_client.settings.breach_provider", "mock")
    breaches = fetch_email_breaches("clean-user@example.com")
    assert breaches == []


def test_fetch_email_breaches_mock_leaked(monkeypatch):
    monkeypatch.setattr("app.services.breach_client.settings.breach_provider", "mock")
    breaches = fetch_email_breaches("leaked-user@example.com")
    assert len(breaches) >= 2
    assert breaches[0].name


def test_watch_preview_endpoint(api):
    import requests

    r = requests.post(
        f"{api}/api/watch/preview",
        json={"email": "leaked-preview@example.com"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["email"] == "leaked-preview@example.com"
    assert isinstance(data["breach_count"], int)
    assert isinstance(data["breaches"], list)


def test_checkout_watch_mock(api, unique_email, db_session):
    import requests

    from app.repositories import watch_repo

    r = requests.post(
        f"{api}/api/checkout",
        json={"tier": "storozh", "email": unique_email},
    )
    assert r.status_code == 200, r.text
    order_id = r.json()["order_id"]
    assert "/watch/success" in r.json()["confirmation_url"]

    result = requests.get(f"{api}/api/orders/{order_id}/result")
    assert result.status_code == 200, result.text
    body = result.json()
    assert body["product_type"] == "watch"
    assert body["monitored_email"] == unique_email.lower()
    assert body["breach_count"] is not None
    assert body["expires_at"]

    sub = watch_repo.get_active_by_email(db_session, unique_email)
    assert sub is not None
    assert sub.status == "active"
