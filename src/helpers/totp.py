import pyotp


def gen_totp(secret: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.now()
