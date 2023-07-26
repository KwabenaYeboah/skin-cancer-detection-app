from django.urls import path

from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, LogoutView,
    PasswordResetConfirmView, PasswordResetCompleteView,)

from .views import (
    SignupView, LoginView,
    AccountVerificationView, ResendVerificationCodeView,
)

urlpatterns = [
    path("signup/",SignupView.as_view(), name="signup"),
    path("activate/", AccountVerificationView.as_view(), name="activate"),
    path("reativate/", ResendVerificationCodeView.as_view(), name='resend'),
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
