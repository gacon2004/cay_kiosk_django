from random import choice
from typing import Any, Dict, Optional

from config import settings  # JWT serializer

# Import các module cần thiết từ Django
from django.contrib.auth import get_user_model  # Lấy model User hiện tại (CustomUser)
from django.contrib.auth.tokens import (
    default_token_generator,
)  # Tạo token reset password
from django.core.mail import send_mail  # Gửi email
from django.db import models  # Query database
from django.template.loader import render_to_string  # Render template email
from django.utils.encoding import force_bytes  # Encode bytes
from django.utils.http import urlsafe_base64_encode  # Encode UID cho URL
from rest_framework import serializers  # Base serializer class
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Lấy model User từ settings.AUTH_USER_MODEL
User = get_user_model()


class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer cho việc đăng nhập.
    Cho phép login bằng username, email hoặc employee_id.
    Kế thừa từ TokenObtainPairSerializer để tạo JWT tokens.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Khởi tạo serializer và customize field labels."""
        super().__init__(*args, **kwargs)
        # Thay đổi label của trường username thành 'username_or_email'
        self.fields[self.username_field] = serializers.CharField(
            label="Username, Email hoặc Employee ID", write_only=True
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate credentials và trả về token nếu hợp lệ.
        Args:
            attrs: Dictionary chứa dữ liệu từ request
        Returns:
            Dict chứa tokens và thông tin user
        Raises:
            ValidationError: Nếu credentials không hợp lệ
        """
        # Lấy username từ attrs (có thể là username, email hoặc employee_id)
        username: Optional[str] = attrs.get(self.username_field)

        # Kiểm tra username có được cung cấp không
        if not username:
            raise serializers.ValidationError(
                {self.username_field: ["Trường này là bắt buộc."]}
            )

        # Tìm user theo username, email hoặc employee_id (case-insensitive)
        try:
            user: User = (
                User.objects.filter(
                    models.Q(username__iexact=username)  # Tìm theo username
                    | models.Q(email__iexact=username)  # Tìm theo email
                    | models.Q(employee_id__iexact=username)  # Tìm theo employee_id
                )
                .distinct()  # Loại bỏ duplicate results
                .get()  # Lấy user duy nhất
            )
        except User.DoesNotExist:
            # Nếu không tìm thấy user, raise error chung chung để bảo mật
            raise serializers.ValidationError(
                {"non_field_errors": ["Thông tin đăng nhập không hợp lệ."]}
            )

        # Kiểm tra password
        password: Optional[str] = attrs.get("password")
        if not password:
            raise serializers.ValidationError({"password": ["Mật khẩu là bắt buộc."]})
        if not user.check_password(password):  # type: ignore
            raise serializers.ValidationError(
                {"non_field_errors": ["Thông tin đăng nhập không hợp lệ."]}
            )

        # Kiểm tra user có active không
        if not user.is_active:  # type: ignore
            raise serializers.ValidationError(
                {"non_field_errors": ["Tài khoản đã bị vô hiệu hóa."]}
            )

        # Tạo JWT tokens
        refresh = self.get_token(user)
        data: Dict[str, Any] = {
            "refresh": str(refresh),  # Refresh token string
            "access": str(refresh.access_token),  # type: ignore  # Access token string
            "user": {  # Thông tin user trả về
                "id": user.id,  # type: ignore
                "username": user.username,  # type: ignore
                "email": user.email,  # type: ignore
                "full_name": user.full_name,  # type: ignore
                "role": user.role,  # type: ignore
                "is_staff": user.is_staff,  # type: ignore
                "is_superuser": user.is_superuser,  # type: ignore
            },
        }

        return data


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer cho việc quên mật khẩu.
    Nhận email và gửi link reset password.
    """

    email = serializers.EmailField(
        required=True, help_text="Email của tài khoản cần reset mật khẩu"
    )

    def validate_email(self, value: str) -> str:
        """
        Validate email tồn tại trong hệ thống.
        """
        try:
            user: User = User.objects.get(
                email__iexact=value
            )  # Tìm user theo email (case-insensitive)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email không tồn tại trong hệ thống.")

        if not user.is_active:  # type: ignore  # Kiểm tra user có active không
            raise serializers.ValidationError("Tài khoản đã bị vô hiệu hóa.")

        return value

    def save(self) -> None:
        """
        Gửi email reset password.
        Tạo token và UID, tạo reset link, render email template và gửi email.
        """
        email: str = self.validated_data["email"]  # Lấy email đã validate
        user: User = User.objects.get(email__iexact=email)  # Lấy user object

        # Tạo token reset password (Django's default token generator)
        token: str = default_token_generator.make_token(user)
        # Encode user ID thành base64 cho URL
        uid: str = urlsafe_base64_encode(force_bytes(user.pk))  # type: ignore

        # Tạo reset link (giả sử frontend có route /reset-password)
        reset_link: str = (
            f"http://localhost:3000/reset-password?uid={uid}&token={token}"
        )

        # Render email template
        subject: str = "Reset mật khẩu - Healthcare Kiosk"
        message: str = render_to_string(
            "emails/reset_password.html",  # Template path
            {
                "user": user,  # User object cho template
                "reset_link": reset_link,  # Reset link
            },
        )

        # Gửi email
        send_mail(
            subject=subject,  # Tiêu đề email
            message=message,  # Nội dung HTML
            from_email=settings.DEFAULT_FROM_EMAIL,  # Email gửi từ
            recipient_list=[email],  # Danh sách nhận email
            html_message=message,  # Phiên bản HTML
        )


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer cho việc reset mật khẩu với token.
    Nhận uid, token, new_password và confirm_password.
    """

    uid = serializers.CharField(required=True)  # UID encoded của user
    token = serializers.CharField(required=True)  # Token reset password
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True,
        help_text="Mật khẩu mới (tối thiểu 8 ký tự)",
    )
    confirm_password = serializers.CharField(
        required=True, write_only=True, help_text="Xác nhận mật khẩu mới"
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate token và password confirmation.
        Args:
            attrs: Dictionary chứa uid, token, passwords
        Returns:
            Dict đã validate với user object thêm vào
        Raises:
            ValidationError: Nếu validation thất bại
        """
        uid: Optional[str] = attrs.get("uid")  # Lấy UID từ request
        token: Optional[str] = attrs.get("token")  # Lấy token từ request
        new_password: Optional[str] = attrs.get("new_password")  # Mật khẩu mới
        confirm_password: Optional[str] = attrs.get(
            "confirm_password"
        )  # Xác nhận mật khẩu

        # Kiểm tra password khớp
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": ["Mật khẩu xác nhận không khớp."]}
            )

        # Validate token
        try:
            from django.utils.encoding import force_str  # Decode bytes thành string
            from django.utils.http import urlsafe_base64_decode  # Decode UID

            if not uid:
                raise ValueError("UID is required")
            user_id: str = force_str(
                urlsafe_base64_decode(uid)
            )  # Decode UID thành user_id
            user: User = User.objects.get(pk=user_id)  # Lấy user từ database
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"token": ["Token không hợp lệ."]})

        # Kiểm tra token có hợp lệ không
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError(
                {"token": ["Token đã hết hạn hoặc không hợp lệ."]}
            )

        # Kiểm tra user có active không
        if not user.is_active:  # type: ignore
            raise serializers.ValidationError(
                {"token": ["Tài khoản đã bị vô hiệu hóa."]}
            )

        attrs["user"] = user  # Thêm user vào validated data
        return attrs

    def save(self) -> User:
        """
        Reset password cho user.
        """
        user: User = self.validated_data["user"]  # Lấy user từ validated data
        new_password: str = self.validated_data["new_password"]  # Lấy mật khẩu mới

        user.set_password(new_password)  # Hash và set password mới
        user.save()  # Lưu user vào database

        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer cho việc đổi mật khẩu (khi đã đăng nhập).
    Nhận old_password, new_password và confirm_password.
    """

    old_password = serializers.CharField(
        required=True, write_only=True, help_text="Mật khẩu cũ"
    )
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True,
        help_text="Mật khẩu mới (tối thiểu 8 ký tự)",
    )
    confirm_password = serializers.CharField(
        required=True, write_only=True, help_text="Xác nhận mật khẩu mới"
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Khởi tạo serializer với user context."""
        self.user: Optional[User] = kwargs.pop("user", None)  # Lấy user từ context
        super().__init__(*args, **kwargs)

    def validate_old_password(self, old_password: str) -> str:
        if not self.user or not self.user.check_password(old_password):  # type: ignore
            raise serializers.ValidationError("Mật khẩu cũ không đúng.")
        return old_password

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate password confirmation.
        """
        new_password: Optional[str] = attrs.get("new_password")  # Lấy mật khẩu mới
        confirm_password: Optional[str] = attrs.get("confirm_password")  # Lấy xác nhận

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": ["Mật khẩu xác nhận không khớp."]}
            )

        return attrs

    def save(self) -> User:
        """
        Đổi mật khẩu cho user.
        """
        new_password: str = self.validated_data[
            "new_password"
        ]  # Lấy mật khẩu mới đã validate
        self.user.set_password(new_password)  # type: ignore  # Hash và set password mới
        self.user.save()  # type: ignore  # Lưu user vào database
        return self.user  # type: ignore


class ProfileUpdateSerializer(serializers.Serializer):
    """
    Serializer cho việc cập nhật profile user.
    Chỉ cho phép cập nhật các trường an toàn.
    """

    first_name = serializers.CharField(max_length=30, required=False, allow_blank=False)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=False)
    address = serializers.CharField(max_length=255, required=False, allow_blank=False)
    role = serializers.CharField(max_length=50, required=False, allow_blank=False)
    department = serializers.CharField(
        max_length=100, required=False, allow_blank=False
    )
    employee_id = serializers.CharField(
        max_length=20, required=False, allow_blank=False
    )
    gender = serializers.BooleanField(required=False)
    dob = serializers.DateField(required=False, allow_null=False)

    def validate_email(self, value: str) -> str:
        """Validate email unique nếu có thay đổi."""
        if hasattr(self, "instance") and self.instance.email != value:  # type: ignore
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email đã được sử dụng.")
        return value

    def validate_employee_id(self, value: str) -> str:
        """Validate employee_id unique nếu có thay đổi."""
        if hasattr(self, "instance") and self.instance.employee_id != value:  # type: ignore
            if User.objects.filter(employee_id=value).exists():
                raise serializers.ValidationError("Mã nhân viên đã tồn tại.")
        return value
