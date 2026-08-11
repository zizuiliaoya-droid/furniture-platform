"""Rate limits for unauthenticated, brute-force-sensitive endpoints."""

from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


class ShareVerifyRateThrottle(AnonRateThrottle):
    scope = 'share_verify'
