"""
VIEW LAYER (Serializers) - Clinic Serializer
Serializers cho Clinic model
"""

from typing import Optional

from apps.kiosk.models import Clinic
from rest_framework import serializers

# Constants cho validation
CLINIC_NAME_MIN_LENGTH = 3
CLINIC_NAME_MAX_LENGTH = 100
CLINIC_ADDRESS_MIN_LENGTH = 10
CLINIC_ADDRESS_MAX_LENGTH = 500


class ClinicNameValidator:
    """Static validator cho clinic name để tái sử dụng"""

    @staticmethod
    def validate_name(name: str, exclude_pk: Optional[int] = None) -> str:
        """
        Validate tên phòng khám với comprehensive rules
        """
        # Strip và validate cơ bản
        cleaned_name = name.strip()

        # Empty check
        if not cleaned_name:
            raise serializers.ValidationError("Tên phòng khám không được để trống")

        # Length validation
        if len(cleaned_name) < CLINIC_NAME_MIN_LENGTH:
            raise serializers.ValidationError(
                f"Tên phòng khám phải có ít nhất {CLINIC_NAME_MIN_LENGTH} ký tự"
            )

        if len(cleaned_name) > CLINIC_NAME_MAX_LENGTH:
            raise serializers.ValidationError(
                f"Tên phòng khám không được vượt quá {CLINIC_NAME_MAX_LENGTH} ký tự"
            )

        # Uniqueness check
        queryset = Clinic.objects.filter(name__iexact=cleaned_name)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)

        if queryset.exists():
            raise serializers.ValidationError("Tên phòng khám đã tồn tại")

        return cleaned_name


class ClinicValidationMixin:
    """
    Mixin class chứa các validation methods cho Clinic serializers
    Sử dụng mixin thay vì base class để linh hoạt hơn
    """

    def validate_name(self, value: str) -> str:
        """
        Validate tên phòng khám
        Args:
            value: Tên phòng khám cần validate
        Returns:
            str: Tên phòng khám đã được validate
        """
        return ClinicNameValidator.validate_name(value)

    def validate_address(self, value: str) -> str:
        """
        Validate địa chỉ phòng khám
        Args:
            value: Địa chỉ cần validate
        Returns:
            str: Địa chỉ đã được validate
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Địa chỉ không được để trống")

        cleaned_address = value.strip()
        if len(cleaned_address) < CLINIC_ADDRESS_MIN_LENGTH:
            raise serializers.ValidationError(
                f"Địa chỉ phải có ít nhất {CLINIC_ADDRESS_MIN_LENGTH} ký tự"
            )

        if len(cleaned_address) > CLINIC_ADDRESS_MAX_LENGTH:
            raise serializers.ValidationError(
                f"Địa chỉ không được vượt quá {CLINIC_ADDRESS_MAX_LENGTH} ký tự"
            )

        return cleaned_address


class ClinicSerializer(ClinicValidationMixin, serializers.ModelSerializer):
    """
    Serializer đầy đủ cho Clinic
    Sử dụng cho detail view và create/update operations
    """

    class Meta:
        model = Clinic
        fields = [
            "id",  # ID tự động tăng
            "name",  # Tên phòng khám
            "is_active",  # Trạng thái (True/False)
            "address",  # Địa chỉ
            "created_at",  # Ngày tạo
            "updated_at",  # Ngày cập nhật
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_active"]


class ClinicListSerializer(serializers.ModelSerializer):
    """
    Serializer rút gọn cho danh sách phòng khám
    Chỉ trả về các fields cần thiết cho list view
    Giúp giảm dung lượng response
    """

    class Meta:
        model = Clinic
        # Chỉ lấy các fields quan trọng
        fields = ["name", "is_active", "address"]


class ClinicCreateSerializer(ClinicValidationMixin, serializers.ModelSerializer):
    """
    Serializer cho tạo phòng khám mới
    Validate các trường bắt buộc
    """

    class Meta:
        model = Clinic
        fields = ["name", "address", "is_active"]


class ClinicUpdateSerializer(ClinicValidationMixin, serializers.ModelSerializer):
    """
    Serializer cho cập nhật phòng khám
    """

    class Meta:
        model = Clinic
        fields = ["name", "address", "is_active"]

    def validate_name(self, value: str) -> str:
        """
        Validate tên phòng khám khi update
        Args:
            value: Tên phòng khám cần validate
        Returns:
            str: Tên phòng khám đã được validate
        """
        # Lấy ID của clinic đang được update để exclude khỏi validation trùng tên
        exclude_pk = self.instance.pk if self.instance else None
        return ClinicNameValidator.validate_name(value, exclude_pk)
