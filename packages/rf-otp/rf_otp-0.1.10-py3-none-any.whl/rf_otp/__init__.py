from .buildOTP import build_otp


def get_otp(secret):
    return build_otp(secret)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        print(get_otp(sys.argv[1]))
