from rest_framework.throttling import ScopedRateThrottle


class OTPThrottle(ScopedRateThrottle):
    scope = "otp"
    rate = "5/minute"
