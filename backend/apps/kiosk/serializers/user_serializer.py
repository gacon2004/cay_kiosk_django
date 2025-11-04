"""
VIEW LAYER (Serializers) - Custom User Serializer
Serializers cho CustomUser model với đầy đủ fields bổ sung
"""

from typing import Any
from rest_framework import serializers
from django.contrib.auth import get_user_model

# Lấy CustomUser model (đã config trong settings.AUTH_USER_MODEL)
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer đầy đủ cho CustomUser
    Dùng để serialize/deserialize dữ liệu User với tất cả fields
    """

    # Custom fields (computed fields)
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)

    class Meta:
        model = User
        fields = [
            # Basic info (từ AbstractUser)
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",  # Computed field
            # Contact info
            "phone",
            "address",
            # Work info
            "role",
            "role_display",  # Human-readable role
            "department",
            "employee_id",
            # Personal info
            "avatar",
            "date_of_birth",
            "gender",
            "gender_display",  # Human-readable gender
            # Status & metadata
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "updated_at",
            # Additional
            "notes",
        ]

        read_only_fields = [
            "id",
            "date_joined",
            "last_login",
            "updated_at",
            "full_name",
            "role_display",
            "gender_display",
        ]

    def get_full_name(self, obj: User) -> str:
        """Trả về họ tên đầy đủ"""
        return obj.full_name


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer đơn giản cho danh sách users
    Chỉ trả về các fields cần thiết để hiển thị trong list
    Giúp giảm dung lượng response khi query nhiều users
    """

    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "role",
            "role_display",
            "department",
            "employee_id",
            "phone",
            "is_active",
            "is_staff",
        ]

    def get_full_name(self, obj: User) -> str:
        return obj.full_name


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer cho tạo user mới
    Xử lý validation password và hash password trước khi lưu
    Hỗ trợ tất cả fields của CustomUser
    """

    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            # Basic info
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            # Contact info
            "phone",
            "address",
            # Work info
            "role",
            "department",
            "employee_id",
            # Personal info
            "date_of_birth",
            "gender",
            # Additional
            "notes",
        ]

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate toàn bộ data trước khi create
        Kiểm tra password và password2 có khớp nhau không
        """
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError({"password2": "Mật khẩu không khớp"})
        return data

    def validate_employee_id(self, value: str) -> str:
        """Validate employee_id không bị trùng"""
        if value and User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Mã nhân viên đã tồn tại")
        return value

    def validate_email(self, value: str) -> str:
        """Validate email không bị trùng"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email đã được sử dụng")
        return value

    def validate_username(self, value: str) -> str:
        """Validate username không bị trùng"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username đã tồn tại")
        return value

    def create(self, validated_data: dict[str, Any]) -> User:
        """
        Override method create để xử lý password
        validated_data: dữ liệu đã qua validation
        """
        validated_data.pop("password2")
        password = validated_data.pop("password")

        # Tạo user với tất cả fields
        user = User.objects.create(**validated_data)
        # Hash password (KHÔNG lưu plain text)
        user.set_password(password)
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer cho cập nhật user
    Cho phép update hầu hết các fields (trừ username, password)
    """

    class Meta:
        model = User
        fields = [
            # Basic info
            "email",
            "first_name",
            "last_name",
            
            # Contact info
            "phone",
            "address",
            
            # Work info
            "role",
            "department",
            "employee_id",
            
            # Personal info
            "avatar",
            "date_of_birth",
            "gender",
            
            # Status
            "is_active",
            
            # Additional
            "notes",
        ]

    def validate_email(self, value: str) -> str:
        """Validate email không bị trùng với user khác"""
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Email đã được sử dụng")
        return value
    
    def validate_employee_id(self, value: str) -> str:
        """Validate employee_id không bị trùng với user khác"""
        user = self.instance
        if value and User.objects.exclude(pk=user.pk).filter(employee_id=value).exists():
            raise serializers.ValidationError("Mã nhân viên đã tồn tại")
        return value
