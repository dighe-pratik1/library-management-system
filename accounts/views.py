import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import RegisterForm, LoginForm, ProfileForm, ResetPasswordForm, StyledPasswordChangeForm
from .models import EmailOTP

User = get_user_model()
OTP_TTL_MINUTES = 5
OTP_RESEND_SECONDS = 60
OTP_MAX_ATTEMPTS = 5

def issue_otp(email, purpose):
    """Create an OTP and send it; remove it if email delivery fails."""
    now = timezone.now()
    if EmailOTP.objects.filter(
        email__iexact=email,
        purpose=purpose,
        created_at__gte=now - timedelta(seconds=OTP_RESEND_SECONDS),
    ).exists():
        raise ValueError("Please wait 60 seconds before requesting another OTP.")

    EmailOTP.objects.filter(email__iexact=email, purpose=purpose).delete()
    code = f"{secrets.randbelow(1_000_000):06d}"
    otp = EmailOTP.objects.create(
        email=email,
        purpose=purpose,
        code_hash=make_password(code),
        expires_at=now + timedelta(minutes=OTP_TTL_MINUTES),
    )
    try:
        sent = send_mail(
            "LibraPro verification code",
            f"Your code is {code}. It expires in {OTP_TTL_MINUTES} minutes. Do not share it.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        if sent != 1:
            raise RuntimeError("Email backend did not confirm the email was sent.")
    except Exception:
        # A failed send must not leave an OTP that blocks an immediate retry.
        EmailOTP.objects.filter(pk=otp.pk).delete()
        raise

def verify_otp(email, purpose, code):
    otp = EmailOTP.objects.filter(email__iexact=email, purpose=purpose).order_by("-created_at").first()
    if not otp or otp.is_expired() or otp.attempts >= OTP_MAX_ATTEMPTS:
        if otp:
            otp.delete()
        return False
    otp.attempts += 1
    otp.save(update_fields=["attempts"])
    if not check_password(code, otp.code_hash):
        return False
    otp.delete()
    return True

def register_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=data["username"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    email=data["email"],
                    password=data["password1"],
                    is_active=False,
                )
        except Exception:
            messages.error(
                request,
                "Account could not be created. The username or email may already exist. "
                "Please check the form and try again.",
            )
            return render(request, "accounts/register.html", {"form": form})

        # Keep the inactive account and session so the user can retry OTP delivery.
        request.session["pending_user_id"] = user.pk
        request.session["otp_purpose"] = "register"
        try:
            issue_otp(user.email, "register")
            messages.success(request, "OTP sent. It expires in 5 minutes.")
        except ValueError as exc:
            messages.warning(request, str(exc))
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Registration OTP email delivery failed")
            messages.error(
                request,
                "Your account was created but the OTP email could not be sent. "
                "Check email settings/server terminal, then try Resend OTP.",
            )
        return redirect("accounts:verify_otp")

    return render(request, "accounts/register.html", {"form": form})

def verify_otp_view(request):
    if request.session.get("otp_purpose") != "register":
        return redirect("accounts:register")
    user = User.objects.filter(pk=request.session.get("pending_user_id"), is_active=False).first()
    if not user:
        request.session.pop("pending_user_id", None)
        request.session.pop("otp_purpose", None)
        return redirect("accounts:register")
    if request.method == "POST":
        code = request.POST.get("otp", "").strip()
        if verify_otp(user.email, "register", code):
            user.is_active = True
            user.save(update_fields=["is_active"])
            request.session.pop("pending_user_id", None)
            request.session.pop("otp_purpose", None)
            login(request, user)
            messages.success(request, "Email verified. Welcome!")
            return redirect(settings.LOGIN_REDIRECT_URL)
        messages.error(request, "OTP is invalid, expired, or already used.")
    return render(request, "accounts/verify_otp.html")

@require_POST
def resend_otp_view(request):
    if request.session.get("otp_purpose") != "register":
        return redirect("accounts:register")
    user = User.objects.filter(pk=request.session.get("pending_user_id"), is_active=False).first()
    if not user:
        return redirect("accounts:register")
    try:
        issue_otp(user.email, "register")
        messages.success(request, "A new OTP was sent.")
    except ValueError as exc:
        messages.warning(request, str(exc))
    except Exception:
        messages.error(request, "Email could not be sent. Check SMTP settings.")
    return redirect("accounts:verify_otp")

def login_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        # Never redirect to an arbitrary external URL supplied in ?next=.
        next_url = request.POST.get("next") or request.GET.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, "accounts/login.html", {"form": form})

@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out.")
    return redirect("accounts:login")

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        # Same response whether or not the account exists.
        messages.info(request, "If an active account exists, a reset OTP will be sent.")
        if user:
            try:
                issue_otp(user.email, "reset")
                request.session["reset_email"] = user.email
                return redirect("accounts:reset_password")
            except ValueError:
                messages.warning(request, "Please wait before requesting another OTP.")
            except Exception:
                messages.error(request, "Email could not be sent. Check SMTP settings.")
        return redirect("accounts:forgot_password")
    return render(request, "accounts/forgot_password.html")

def reset_password_view(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("accounts:forgot_password")
    form = ResetPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if verify_otp(email, "reset", form.cleaned_data["otp"]):
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user:
                user.set_password(form.cleaned_data["password1"])
                user.save(update_fields=["password"])
                request.session.pop("reset_email", None)
                messages.success(request, "Password updated. Please log in.")
                return redirect("accounts:login")
        messages.error(request, "OTP is invalid, expired, or already used.")
    return render(request, "accounts/reset_password.html", {"form": form})

@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})

@login_required
def change_password_view(request):
    form = StyledPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password changed successfully.")
        return redirect("accounts:profile")
    return render(request, "accounts/change_password.html", {"form": form})
