"""
CONTROLLER LAYER - Authentication Views (Controllers)
Xử lý HTTP requests/responses, gọi service layer cho business logic
"""

from typing import Any, Dict

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializer import ChangePasswordSerializer  # type: ignore
from .serializer import (
    ForgotPasswordSerializer,
    ProfileUpdateSerializer,
    ResetPasswordSerializer,
)
from .service import AuthenticationService


class CustomTokenRefreshView(TokenRefreshView):
    """
    CONTROLLER - Custom Token Refresh View
    Override để customize error handling
    """

    def post(self, request, *args, **kwargs):
        """
        POST /auth/refresh/
        Refresh access token từ refresh token
        """
        # Validate input
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "refresh token là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Gọi parent method
        try:
            response = super().post(request, *args, **kwargs)
            # Thêm thông tin bổ sung nếu cần
            response.data["message"] = "Token refreshed successfully"
            return response
        except Exception as e:
            return Response(
                {"error": f"Không thể refresh token: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class AuthAPIRootView(APIView):
    """
    API Root view cho Authentication endpoints.
    Trả về thông tin về các endpoints available.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request) -> Response:
        """
        GET /api/auth/
        Trả về danh sách các authentication endpoints available.
        """
        return Response(
            {
                "message": "Authentication API",
                "version": "1.0",
                "endpoints": {
                    "login": {
                        "url": "/api/auth/login",
                        "method": "POST",
                        "description": "Đăng nhập và nhận JWT tokens",
                    },
                    "logout": {
                        "url": "/api/auth/logout",
                        "method": "POST",
                        "description": "Đăng xuất và blacklist token",
                        "auth_required": True,
                    },
                    "forgot_password": {
                        "url": "/api/auth/forgot-password",
                        "method": "POST",
                        "description": "Gửi email reset mật khẩu",
                    },
                    "reset_password": {
                        "url": "/api/auth/reset-password",
                        "method": "POST",
                        "description": "Reset mật khẩu từ token",
                    },
                    "token_refresh": {
                        "url": "/api/auth/token/refresh",
                        "method": "POST",
                        "description": "Refresh JWT access token",
                    },
                    "profile": {
                        "url": "/api/auth/profile",
                        "method": "GET, PUT",
                        "description": "Xem và cập nhật thông tin profile",
                        "auth_required": True,
                    },
                    "change_password": {
                        "url": "/api/auth/change-password",
                        "method": "POST",
                        "description": "Đổi mật khẩu khi đã đăng nhập",
                        "auth_required": True,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    """
    CONTROLLER - API đăng nhập
    Service: AuthenticationService.login_user()
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request) -> Response:
        """
        POST /api/auth/login
        Đăng nhập và trả về JWT tokens
        """
        # Lấy dữ liệu từ request
        username = request.data.get("username")
        password = request.data.get("password")

        # Validate input cơ bản
        if not username or not password:
            return Response(
                {"error": "Username và password là bắt buộc."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Gọi service để xử lý login
        success, result = AuthenticationService.login_user(username, password)

        if success:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": result["error"]}, status=status.HTTP_401_UNAUTHORIZED
            )


class ForgotPasswordView(APIView):
    """
    CONTROLLER - API quên mật khẩu
    DTO: ForgotPasswordSerializer
    Service: AuthenticationService.forgot_password()
    """

    def post(self, request) -> Response:
        """
        POST /auth/forgot-password/
        Gửi email reset mật khẩu
        """
        # Validate input qua DTO
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Gọi service để gửi email
        success, message = AuthenticationService.forgot_password(
            email=serializer.validated_data["email"]
        )

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    CONTROLLER - API reset mật khẩu
    DTO: ResetPasswordSerializer
    Service: AuthenticationService.reset_password()
    """

    # permission_classes = [permissions.AllowAny]

    def post(self, request) -> Response:
        """
        POST /auth/reset-password/
        Reset mật khẩu từ token
        """
        # Validate input qua DTO
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Gọi service để reset password
        success, message = AuthenticationService.reset_password(
            uid=serializer.validated_data["uid"],
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
            confirm_password=serializer.validated_data["confirm_password"],
        )

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


# Lấy profile của user hiện tại
class ProfileView(APIView):
    """
    CONTROLLER - API quản lý profile
    DTO: ProfileUpdateSerializer
    Service: AuthenticationService.get_user_profile(), update_user_profile()
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) -> Response:
        """
        GET /auth/profile/
        Lấy thông tin profile của user hiện tại
        """
        # Gọi service để lấy profile
        profile_data = AuthenticationService.get_user_profile(request.user)
        return Response(profile_data, status=status.HTTP_200_OK)

    def put(self, request) -> Response:
        """
        PUT /auth/profile/
        Cập nhật thông tin profile
        """
        # Validate input qua DTO
        serializer = ProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Gọi service để cập nhật profile
        success, result = AuthenticationService.update_user_profile(
            user=request.user, data=serializer.validated_data
        )

        if success:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    CONTROLLER - API đổi mật khẩu
    DTO: ChangePasswordSerializer
    Service: AuthenticationService.change_password()
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request) -> Response:
        """
        POST /auth/change-password/
        Đổi mật khẩu khi đã đăng nhập
        """
        # Validate input qua DTO
        serializer = ChangePasswordSerializer(data=request.data, user=request.user)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Gọi service để đổi mật khẩu
        success, message = AuthenticationService.change_password(
            user=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
            confirm_password=serializer.validated_data["confirm_password"],
        )

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    CONTROLLER - API đăng xuất
    DTO: Không cần (chỉ cần refresh_token)
    Service: AuthenticationService.logout_user()
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request) -> Response:
        """
        POST /auth/logout/
        Blacklist refresh token để đăng xuất
        """
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "refresh_token là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Gọi service để logout
        success, message = AuthenticationService.logout_user(refresh_token)

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
