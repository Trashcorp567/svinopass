from app.services.email import send_password_email

ok = send_password_email(
    to="vladlen567@gmail.com",
    password="TEST-DKIM",
    tier_name="Test",
    order_id="test-dkim",
)
print("sent:", ok)
