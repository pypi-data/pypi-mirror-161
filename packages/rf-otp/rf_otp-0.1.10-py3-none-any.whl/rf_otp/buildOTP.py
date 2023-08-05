import pyotp


# Get secret code of 6 digits
#
# Parameters:
# secret: Secret code of x digits
def build_otp(secret):
    key = None
    try:
        totp = pyotp.TOTP(secret)
        key = totp.now()
    finally:
        return key
