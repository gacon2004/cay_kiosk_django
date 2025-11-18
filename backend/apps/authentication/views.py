"""
CONTROLLER LAYER - Authentication Views (Controllers)
Xử lý HTTP requests/responses, gọi service layer cho business logic
"""

from typing import Any, Dict

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from django.db import models

from .serializer import ChangePasswordSerializer  # type: ignore
from .serializer import (
    ForgotPasswordSerializer,
    ProfileUpdateSerializer,
    ResetPasswordSerializer,
)
from apps.kiosk.models import CustomUser

class CustomTokenRefreshView(TokenRefreshView):
    """
    CONTROLLER - Custom Token Refresh View
    Override để customize error handling
    """

    def post(self, request, *args, **kwargs):
        """
        POST /auth/refresh
        Refresh access token từ refresh token
        """
        # Validate input
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "refresh token là bắt buộc"},status=status.HTTP_400_BAD_REQUEST,)

        # Gọi parent method
        try:
            response = super().post(request, *args, **kwargs)
            # Thêm thông tin bổ sung
            response.data["message"] = "Token refreshed successfully"
            return response
        except Exception as e:
            return Response(
                {"error": f"Không thể refresh token: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            
class LoginView(APIView):
    """
    CONTROLLER - API đăng nhập
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request) -> Response:
        """
        POST /api/auth/login
        Đăng nhập và trả về JWT tokens
        """
        # Lấy dữ liệu từ request
        username: str = request.data.get("username")
        password: str = request.data.get("password")
        # Validate input cơ bản
        if not username or not password:
            return Response(
                {"error": "Username và password là bắt buộc."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user: CustomUser = (
                CustomUser.objects.filter(
                    models.Q(username__iexact=username)  # Tìm theo username
                    | models.Q(email__iexact=username)  # Tìm theo email
                )
                .distinct()  # Loại bỏ duplicate results
                .get()  # Lấy user duy nhất
            )
        except CustomUser.DoesNotExist:
            return Response({"success": False, "error": "Thông tin đăng nhập không hợp lệ."} , status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(password):  # type: ignore
            return Response({"success": False, "error": "Thông tin đăng nhập không hợp lệ."} , status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:  # type: ignore
            return Response({"success": False, "error": "Tài khoản đã bị vô hiệu hóa."}, status=status.HTTP_401_UNAUTHORIZED)
        # Tạo JWT tokens
        refresh = RefreshToken.for_user(user)
        data: Dict[str, Any] = {
            "refresh": str(refresh),  # Refresh token string
            "access": str(refresh.access_token),  # type: ignore  # Access token string
            "user": {  # Thông tin user trả về
                "username": str(user.username),
                "email": str(user.email), 
                "full_name": str(user.full_name), 
                "role": str(user.role),
                "is_staff": user.is_staff,  # type: ignore
                "is_superuser": user.is_superuser,  # type: ignore
            },
        }
        return Response(data, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    """
    CONTROLLER - API quên mật khẩu
    DTO: ForgotPasswordSerializer
    """

    def post(self, request) -> Response:
        """
        POST /auth/forgot-password Gửi email reset mật khẩu
        """
        # Validate input qua DTO
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        if not email or "@" not in email:
            return Response({"success": False, "error": "Email không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        # Tìm user theo email
        try:
            user: CustomUser = CustomUser.objects.get(email__iexact=email)
        except CustomUser.DoesNotExist:
            # Để bảo mật, không tiết lộ user có tồn tại hay không
            return Response({"message": "Nếu email tồn tại trong hệ thống, bạn sẽ nhận được hướng dẫn reset mật khẩu."},status=status.HTTP_200_OK)

        # Kiểm tra user có active không
        if not user.is_active:  # type: ignore
            return Response({"message": "Nếu email tồn tại trong hệ thống, bạn sẽ nhận được hướng dẫn reset mật khẩu."},status=status.HTTP_200_OK)

        # Tạo token reset password
        uid = urlsafe_base64_encode(force_bytes(user.pk))  # type: ignore
        token = default_token_generator.make_token(user)

        # Tạo context cho email template
        reset_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/reset-password?uid={uid}&token={token}"
        context = {
            "user": user,
            "uid": uid,
            "token": token,
            "reset_url": reset_url,
            "domain": settings.FRONTEND_URL or "localhost:3000",
            "protocol": (
                "https"
                if settings.FRONTEND_URL and "https://" in settings.FRONTEND_URL
                else "http"
            ),
        }

        # Render email content
        try:
            subject = "Password Reset - Healthcare Kiosk"
            # Plain text version (nếu có template riêng)
            message = render_to_string(
                "authentication/reset_password_email.txt", context
            )
            # HTML version
            html_message = render_to_string(
                "authentication/reset_password_email.html", context
            )

            # Gửi email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,  # Sử dụng settings
                recipient_list=[user.email],  # type: ignore
                html_message=html_message,
                fail_silently=False,
            )

            return Response({"success": True, "message": "Email reset mật khẩu đã được gửi. Vui lòng kiểm tra hộp thư."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"success": False, "error": f"Lỗi khi gửi email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordView(APIView):
    """
    CONTROLLER - API reset mật khẩu DTO: ResetPasswordSerializer
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request) -> Response:
        """
        POST /auth/reset-password
        Reset mật khẩu từ token
        """
        # Validate input qua DTO
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        uid=serializer.validated_data["uid"] #uid: UID encoded của user
        token=serializer.validated_data["token"] #token: Token reset password
        new_password=serializer.validated_data["new_password"]
        confirm_password=serializer.validated_data["confirm_password"]
        # Validate input
        if not new_password or len(new_password) < 8:
            return Response({"error": "Mật khẩu mới phải có ít nhất 8 ký tự.", "code": 1000}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "Mật khẩu xác nhận không khớp.", "code": 1001}, status=status.HTTP_400_BAD_REQUEST)

        # Decode uid để lấy user id
        try:
            uid_int = urlsafe_base64_decode(uid).decode()
            user_id = int(uid_int)
        except (ValueError, TypeError):
            return Response({"error": "Link reset mật khẩu không hợp lệ.", "code": 1002}, status=status.HTTP_400_BAD_REQUEST)

        # Tìm user
        try:
            user: CustomUser = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"success": False,"error": "Link reset mật khẩu không hợp lệ.", "code": 1003}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra user có active không
        if not user.is_active:  # type: ignore
            return Response({"success": False,"error": "Tài khoản đã bị vô hiệu hóa."}, status=status.HTTP_400_BAD_REQUEST)
        # Validate token
        if not default_token_generator.check_token(user, token):
            return Response({"success": False,"error": "Token reset mật khẩu không hợp lệ hoặc đã hết hạn."}, status=status.HTTP_400_BAD_REQUEST)

        # Đặt mật khẩu mới
        try:
            user.set_password(new_password)  # type: ignore
            user.save()  # type: ignore
            return Response({"message": "Mật khẩu đã được đặt lại thành công."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Lỗi khi reset mật khẩu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Lấy profile của user hiện tại
class ProfileView(APIView):
    """
    CONTROLLER - API quản lý profile, DTO: ProfileUpdateSerializer
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        """
        GET /auth/profile, Lấy thông tin profile của user hiện tại
        """
        # Gọi service để lấy profile
        profile_data: CustomUser = request.user  # type: ignore
        return Response(profile_data, status=status.HTTP_200_OK)

    def put(self, request) -> Response:
        """
        PUT /auth/profile, Cập nhật thông tin profile
        """
        # Validate input qua DTO
        serializer = ProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user: CustomUser = request.user
        data: Dict[str, Any] = serializer.validated_data
        # Các trường được phép cập nhật
        allowed_fields = ["first_name","last_name","email",
            "phone", "address", "role","department",
            "employee_id","gender","dob"]

        # Validate email unique nếu có thay đổi
        if "email" in data and data["email"] != user.email:  # type: ignore
            if CustomUser.objects.filter(email=data["email"]).exists():
                return Response({"success": False, "errors": {"email": "Email đã tồn tại."}}, status=status.HTTP_400_BAD_REQUEST)
        # Validate employee_id unique nếu có thay đổi
        if "employee_id" in data and data["employee_id"] != user.employee_id:  # type: ignore
            if CustomUser.objects.filter(employee_id=data["employee_id"]).exists():
                return Response({"success": False, "errors": {"employee_id": "Nhân viên đã tồn tại."}}, status=status.HTTP_400_BAD_REQUEST)

        # Cập nhật các trường
        print("debug:", data.items())
        for field, value in data.items():
            if field in allowed_fields:
                setattr(user, field, value)
        try:
            user.save()
            # Trả về thông tin user đã cập nhật
            return Response(ProfileUpdateSerializer(user).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"errors": f"Lỗi khi cập nhật: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangePasswordView(APIView):
    """
    CONTROLLER - API đổi mật khẩu, DTO: ChangePasswordSerializer
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        """
        POST /auth/change-password, Đổi mật khẩu khi đã đăng nhập
        """
        # Validate input qua DTO
        serializer = ChangePasswordSerializer(data=request.data, user=request.user)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user: CustomUser=request.user
        old_password=serializer.validated_data["old_password"]
        new_password=serializer.validated_data["new_password"]
        confirm_password=serializer.validated_data["confirm_password"]     
        # Validate input
        if not old_password:
            return Response({"success": False,"error": "Mật khẩu cũ là bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)

        if not new_password or len(new_password) < 8:
            return Response({"success": False,"error": "Mật khẩu mới phải có ít nhất 8 ký tự."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"success": False,"error": "Mật khẩu xác nhận không khớp."}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra mật khẩu cũ
        if not user.check_password(old_password):  # type: ignore
            return Response({"success": False,"error": "Mật khẩu cũ không đúng."}, status=status.HTTP_400_BAD_REQUEST)
        # Kiểm tra mật khẩu mới khác mật khẩu cũ
        if user.check_password(new_password):  # type: ignore
            return Response({"success": False,"error": "Mật khẩu mới phải khác mật khẩu cũ."}, status=status.HTTP_400_BAD_REQUEST)

        # Đặt mật khẩu mới
        try:
            user.set_password(new_password)  # type: ignore
            user.save()  # type: ignore
            return Response({"success": True,"message": "Mật khẩu đã được đổi thành công."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False,"errors": f"Lỗi khi đổi mật khẩu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    """
    CONTROLLER - API đăng xuất, DTO: Không cần (chỉ cần refresh_token)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        """
        POST /auth/logout, Blacklist refresh token để đăng xuất
        """
        refresh_token: str = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "refresh_token là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)  # type: ignore
            token.blacklist()
            return Response({"success": True,"message": "Đăng xuất thành công."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False,"error": f"Lỗi khi đăng xuất: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
