import re

from app.services.passphrase import generate_passphrase


def test_generate_passphrase_format():
    phrase = generate_passphrase()
    parts = phrase.split("-")
    assert len(parts) >= 5
    assert re.search(r"\d", parts[-1])
    assert re.search(r"[!@#$%^&*\-_=+?]", parts[-1])


def test_generate_passphrase_unique():
    phrases = {generate_passphrase() for _ in range(20)}
    assert len(phrases) >= 18
