"""
SERVICE LAYER - Authentication Services
Chứa business logic cho authentication operations
"""

from typing import Any, Dict, Optional, Tuple

from apps.kiosk.models.user import CustomUser
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework_simplejwt.tokens import RefreshToken

# User = get_user_model()


class AuthenticationService:

    @staticmethod
    def login_user(username: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Xử lý logic đăng nhập user.

        Args:
            username: Username, email hoặc employee_id
            password: Mật khẩu

        Returns:
            Tuple (success: bool, data: Dict)
            - success=True: {'refresh': str, 'access': str, 'user': dict}
            - success=False: {'error': str}
        """
        # Tìm user theo username, email hoặc employee_id (case-insensitive)
        try:
            user: CustomUser = (
                CustomUser.objects.filter(
                    models.Q(username__iexact=username)  # Tìm theo username
                    | models.Q(email__iexact=username)  # Tìm theo email
                    | models.Q(employee_id__iexact=username)  # Tìm theo employee_id
                )
                .distinct()  # Loại bỏ duplicate results
                .get()  # Lấy user duy nhất
            )
        except CustomUser.DoesNotExist:
            # Nếu không tìm thấy user, raise error chung chung để bảo mật
            return False, {"error": "Thông tin đăng nhập không hợp lệ."}

        # Kiểm tra password
        if not user.check_password(password):  # type: ignore
            return False, {"error": "Thông tin đăng nhập không hợp lệ."}

        # Kiểm tra user có active không
        if not user.is_active:  # type: ignore
            return False, {"error": "Tài khoản đã bị vô hiệu hóa."}

        # Tạo JWT tokens
        refresh = RefreshToken.for_user(user)
        data: Dict[str, Any] = {
            "refresh": str(refresh),  # Refresh token string
            "access": str(refresh.access_token),  # type: ignore  # Access token string
            "user": {  # Thông tin user trả về
                "username": user.username,  # type: ignore
                "email": user.email,  # type: ignore
                "full_name": user.full_name,  # type: ignore
                "role": user.role,  # type: ignore
                "is_staff": user.is_staff,  # type: ignore
                "is_superuser": user.is_superuser,  # type: ignore
            },
        }

        return True, data

    @staticmethod
    def forgot_password(email: str) -> Tuple[bool, str]:
        """
        Xử lý logic quên mật khẩu.
        """
        # Validate email format
        if not email or "@" not in email:
            return False, "Email không hợp lệ."

        # Tìm user theo email
        try:
            user: CustomUser = CustomUser.objects.get(email__iexact=email)
        except CustomUser.DoesNotExist:
            # Để bảo mật, không tiết lộ user có tồn tại hay không
            return (
                True,
                "Nếu email tồn tại trong hệ thống, bạn sẽ nhận được hướng dẫn reset mật khẩu.",
            )

        # Kiểm tra user có active không
        if not user.is_active:  # type: ignore
            return (
                True,
                "Nếu email tồn tại trong hệ thống, bạn sẽ nhận được hướng dẫn reset mật khẩu.",
            )

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

            return True, "Email reset mật khẩu đã được gửi. Vui lòng kiểm tra hộp thư."

        except Exception as e:
            return False, f"Lỗi khi gửi email: {str(e)}"

    @staticmethod
    def reset_password(
        uid: str, token: str, new_password: str, confirm_password: str
    ) -> Tuple[bool, str]:
        """
        Xử lý logic reset mật khẩu với token.

        Args:
            uid: UID encoded của user
            token: Token reset password
            new_password: Mật khẩu mới
            confirm_password: Xác nhận mật khẩu mới

        Returns:
            Tuple (success: bool, message: str)
        """
        # Validate input
        if not new_password or len(new_password) < 8:
            return False, "Mật khẩu mới phải có ít nhất 8 ký tự."

        if new_password != confirm_password:
            return False, "Mật khẩu xác nhận không khớp."

        # Decode uid để lấy user id
        try:
            uid_int = urlsafe_base64_decode(uid).decode()
            user_id = int(uid_int)
        except (ValueError, TypeError):
            return False, "Link reset mật khẩu không hợp lệ."

        # Tìm user
        try:
            user: CustomUser = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return False, "Link reset mật khẩu không hợp lệ."

        # Kiểm tra user có active không
        if not user.is_active:  # type: ignore
            return False, "Tài khoản đã bị vô hiệu hóa."

        # Validate token
        if not default_token_generator.check_token(user, token):
            return False, "Token reset mật khẩu không hợp lệ hoặc đã hết hạn."

        # Đặt mật khẩu mới
        try:
            user.set_password(new_password)  # type: ignore
            user.save()  # type: ignore
            return True, "Mật khẩu đã được reset thành công."
        except Exception as e:
            return False, f"Lỗi khi reset mật khẩu: {str(e)}"

    @staticmethod
    def change_password(
        user: CustomUser, old_password: str, new_password: str, confirm_password: str
    ) -> Tuple[bool, str]:
        """
        Xử lý logic đổi mật khẩu khi đã đăng nhập.

        Args:
            user: CustomUser object hiện tại
            old_password: Mật khẩu cũ
            new_password: Mật khẩu mới
            confirm_password: Xác nhận mật khẩu mới

        Returns:
            Tuple (success: bool, message: str)
        """
        # Validate input
        if not old_password:
            return False, "Vui lòng nhập mật khẩu cũ."

        if not new_password or len(new_password) < 8:
            return False, "Mật khẩu mới phải có ít nhất 8 ký tự."

        if new_password != confirm_password:
            return False, "Mật khẩu xác nhận không khớp."

        # Kiểm tra mật khẩu cũ
        if not user.check_password(old_password):  # type: ignore
            return False, "Mật khẩu cũ không đúng."

        # Kiểm tra mật khẩu mới khác mật khẩu cũ
        if user.check_password(new_password):  # type: ignore
            return False, "Mật khẩu mới phải khác mật khẩu cũ."

        # Đặt mật khẩu mới
        try:
            user.set_password(new_password)  # type: ignore
            user.save()  # type: ignore
            return True, "Mật khẩu đã được thay đổi thành công."
        except Exception as e:
            return False, f"Lỗi khi đổi mật khẩu: {str(e)}"

    @staticmethod
    def get_user_profile(user: CustomUser) -> Dict[str, Any]:
        """
        Lấy thông tin profile của user.

        Args:
            user: CustomUser object

        Returns:
            Dict chứa thông tin profile
        """
        return {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role,
            "department": user.department,
            "employee_id": user.employee_id,
            "phone": user.phone,
            "address": user.address,
            "gender": user.gender,
            "dob": user.dob,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
        }

    @staticmethod
    def update_user_profile(
        user: CustomUser, data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Cập nhật thông tin profile của user.

        Args:
            user: User object
            data: Dict chứa dữ liệu cập nhật

        Returns:
            Tuple (success: bool, result: Dict)
            - success=True: {'user': updated_user_data}
            - success=False: {'errors': validation_errors}
        """
        # Các trường được phép cập nhật
        allowed_fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "role",
            "department",
            "employee_id",
            "gender",
            "dob",
        ]

        # Validate email unique nếu có thay đổi
        if "email" in data and data["email"] != user.email:  # type: ignore
            if CustomUser.objects.filter(email=data["email"]).exists():
                return False, {"errors": {"email": ["Email đã được sử dụng."]}}

        # Validate employee_id unique nếu có thay đổi
        if "employee_id" in data and data["employee_id"] != user.employee_id:  # type: ignore
            if CustomUser.objects.filter(employee_id=data["employee_id"]).exists():
                return False, {"errors": {"employee_id": ["Mã nhân viên đã tồn tại."]}}

        # Cập nhật các trường
        for field, value in data.items():
            if field in allowed_fields:
                setattr(user, field, value)

        try:
            user.save()
            # Trả về thông tin user đã cập nhật
            updated_data = AuthenticationService.get_user_profile(user)
            return True, {"user": updated_data}
        except Exception as e:
            return False, {"errors": {"general": [f"Lỗi khi cập nhật: {str(e)}"]}}

    @staticmethod
    def logout_user(refresh_token: str) -> Tuple[bool, str]:
        """
        Xử lý logic đăng xuất user (blacklist token).

        Args:
            refresh_token: Refresh token cần blacklist

        Returns:
            Tuple (success: bool, message: str)
        """
        try:
            token = RefreshToken(refresh_token)  # type: ignore
            token.blacklist()
            return True, "Đăng xuất thành công."
        except Exception as e:
            return False, f"Lỗi khi đăng xuất: {str(e)}"
