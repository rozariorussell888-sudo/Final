from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.login,
        name="login",
    ),
    path(
        "signup/",
        views.signup,
        name="signup",
    ),
    path(
        "verify-signup-otp/",
        views.verify_signup_otp,
        name="verify_signup_otp",
    ),
    path(
        "home/",
        views.home,
        name="home",
    ),
    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password",
    ),
    path(
        "verify-otp/",
        views.verify_otp,
        name="verify_otp",
    ),
    path(
        "reset-password/",
        views.reset_password,
        name="reset_password",
    ),
]