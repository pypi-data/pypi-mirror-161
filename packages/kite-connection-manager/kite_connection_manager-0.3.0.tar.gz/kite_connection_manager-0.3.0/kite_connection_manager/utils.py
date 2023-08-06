import pyotp


def get_totp(secret: str) -> str:
    """
    Fetches the T-OTP from Google Authenticator
    """
    return pyotp.TOTP(secret).now()
