from typing import TYPE_CHECKING, cast

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

if TYPE_CHECKING:
    from apps.kiosk.models import CustomUser

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """API đăng ký user mới"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data

        # Kiểm tra username đã tồn tại
        if User.objects.filter(username=data.get("username")).exists():
            return Response(
                {"error": "Username đã tồn tại!"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Kiểm tra email đã tồn tại
        if User.objects.filter(email=data.get("email")).exists():
            return Response(
                {"error": "Email đã được sử dụng!"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Kiểm tra password khớp
        if data.get("password") != data.get("password2"):
            return Response(
                {"error": "Mật khẩu không khớp!"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Tạo user mới
        try:
            user = cast(
                "CustomUser",
                User.objects.create(
                    username=data.get("username"),
                    email=data.get("email"),
                    first_name=data.get("first_name", ""),
                    last_name=data.get("last_name", ""),
                    password=make_password(data.get("password")),
                ),
            )

            return Response(
                {
                    "message": "Đăng ký thành công!",
                    "user": {
                        "user_id": user.pk,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """API đăng nhập - trả về JWT token"""

    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):
    """API xem và cập nhật profile"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """GET: Lấy thông tin profile"""
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
                "last_login": user.last_login,
            }
        )

    def put(self, request):
        """PUT: Cập nhật profile"""
        user = request.user
        data = request.data

        # Cập nhật thông tin
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.email = data.get("email", user.email)
        user.save()

        return Response(
            {
                "message": "Cập nhật profile thành công!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            }
        )


class ChangePasswordView(APIView):
    """API đổi mật khẩu"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        # Kiểm tra mật khẩu cũ
        if not user.check_password(data.get("old_password")):
            return Response(
                {"error": "Mật khẩu cũ không đúng!"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Kiểm tra mật khẩu mới khớp
        if data.get("new_password") != data.get("new_password2"):
            return Response(
                {"error": "Mật khẩu mới không khớp!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Đổi mật khẩu
        user.set_password(data.get("new_password"))
        user.save()

        return Response({"message": "Đổi mật khẩu thành công!"})


class LogoutView(APIView):
    """API logout - blacklist token"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Đăng xuất thành công!"})
        except Exception as e:
            return Response(
                {"error": "Token không hợp lệ!"}, status=status.HTTP_400_BAD_REQUEST
            )
