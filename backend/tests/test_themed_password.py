import re

import pytest

from app.services.backup_codes import BACKUP_PREFIXES, generate_backup_codes
from app.services.password import generate_password, password_contains_theme
from app.services.uniqueness import claim_credential, claim_unique


def test_generate_password_contains_theme():
    password = generate_password("bacon", 24)
    assert len(password) == 24
    assert password_contains_theme(password)
    assert re.search(r"[a-z]", password)
    assert re.search(r"[A-Z]", password)
    assert re.search(r"\d", password)
    assert re.search(r"[!@#$%^&*\-_=+?]", password)


def test_generate_password_svinomat_length():
    password = generate_password("svinomat", 20)
    assert len(password) == 20
    assert password_contains_theme(password)


def test_claim_unique_retries(monkeypatch):
    def always_reject(_value: str) -> bool:
        return False

    monkeypatch.setattr("app.services.uniqueness.claim_credential", always_reject)

    def always_same():
        return "Sv1n0-fixed"

    with pytest.raises(RuntimeError):
        claim_unique(always_same)

    accepted: list[str] = []

    def accept_once(value: str) -> bool:
        if value in accepted:
            return False
        accepted.append(value)
        return True

    monkeypatch.setattr("app.services.uniqueness.claim_credential", accept_once)

    def alternating():
        return f"Sv1n0-{len(accepted)}"

    value = claim_unique(alternating)
    assert value.startswith("Sv1n0-")


def test_backup_codes_have_themed_prefix():
    codes = generate_backup_codes(count=5, length=10)
    assert all(len(code) == 10 for code in codes)
    assert all(code[:2] in BACKUP_PREFIXES for code in codes)
    assert len(set(codes)) == 5


def test_claim_credential_integration():
    import uuid

    token = f"Sv1n0-test-unique-{uuid.uuid4().hex}"
    assert claim_credential(token) is True
    assert claim_credential(token) is False
