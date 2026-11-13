"""Protect all library modules by default; authentication endpoints stay public."""
from django.conf import settings
from django.contrib.auth.views import redirect_to_login


class LoginRequiredMiddleware:
    """Require an authenticated session for application pages outside public paths."""
    EXEMPT_PREFIXES = (
        "/accounts/login/",
        "/accounts/register/",
        "/accounts/verify-otp/",
        "/accounts/resend-otp/",
        "/accounts/forgot-password/",
        "/accounts/reset-password/",
        "/admin/",
        "/static/",
        "/media/",
        "/favicon.ico",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info or "/"
        if (not request.user.is_authenticated
                and not any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES)):
            return redirect_to_login(path, settings.LOGIN_URL)
        return self.get_response(request)
