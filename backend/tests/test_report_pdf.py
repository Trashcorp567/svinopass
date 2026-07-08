from datetime import datetime, timezone

import pytest

from app.services.report_pdf import build_svino_report_pdf


def test_build_svino_report_pdf_bytes():
    pdf = build_svino_report_pdf(
        order_id="12345678-abcd-efgh-ijkl-123456789abc",
        tier_name="Легенда хрюши",
        paid_at=datetime(2026, 7, 8, 12, 0, tzinfo=timezone.utc),
        entropy_bits=128.5,
        password_length=32,
        generation_mode="random",
    )
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 500


def test_build_svino_report_pdf_rejects_password():
    with pytest.raises(ValueError, match="Password must not"):
        build_svino_report_pdf(
            order_id="12345678-abcd-efgh-ijkl-123456789abc",
            tier_name="Легенда хрюши",
            paid_at=None,
            entropy_bits=100.0,
            password_length=32,
            generation_mode="random",
            password="SecretPassword123!",
        )


def test_build_svino_report_pdf_no_password_in_content():
    secret = "SuperSecretLegendPassword99!"
    pdf = build_svino_report_pdf(
        order_id="12345678-abcd-efgh-ijkl-123456789abc",
        tier_name="Легенда хрюши",
        paid_at=None,
        entropy_bits=100.0,
        password_length=len(secret),
        generation_mode="random",
    )
    assert secret.encode() not in pdf
