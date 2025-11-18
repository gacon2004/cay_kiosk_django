from django.urls import path

from .views import (
    ChangePasswordView,
    CustomTokenRefreshView,
    ForgotPasswordView,
    LoginView,
    LogoutView,
    ProfileView,
    ResetPasswordView,
)

app_name = "authentication"

urlpatterns = [
    # Authentication endpoints
    path("/login", LoginView.as_view(), name="login"),
    path("/forgot-password", ForgotPasswordView.as_view(), name="forgot_password"),
    path("/reset-password", ResetPasswordView.as_view(), name="reset_password"),
    path("/logout", LogoutView.as_view(), name="logout"),
    path("/refresh", CustomTokenRefreshView.as_view(), name="token_refresh"),
    # Profile endpoints
    path("/profile", ProfileView.as_view(), name="profile"),
    path("/change-password", ChangePasswordView.as_view(), name="change_password"),
]
