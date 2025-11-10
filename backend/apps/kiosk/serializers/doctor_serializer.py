"""
VIEW LAYER (Serializers) - Doctor Serializer
Chuyển đổi Doctor model thành JSON và validate input
"""

from typing import Optional

from apps.kiosk.models import Doctors
from rest_framework import serializers

# Constants cho validation
DOCTOR_ID_PREFIX = "BS"
MAX_YEARS_EXPERIENCE = 60
MIN_YEARS_EXPERIENCE = 0


class DoctorValidators:
    @staticmethod
    def validate_doctor_id(doctor_id: str) -> str:
        # check id empty
        if not doctor_id:
            raise serializers.ValidationError("Mã bác sĩ không được để trống")
        # Clean and standardize ID
        cleaned_id = doctor_id.strip().upper()

        if not cleaned_id.startswith(DOCTOR_ID_PREFIX):
            raise serializers.ValidationError(
                f"Mã bác sĩ phải bắt đầu bằng '{DOCTOR_ID_PREFIX}'"
            )

        # Check format: BS + numbers (e.g., BS001, BS123)
        if len(cleaned_id) < 3 or not cleaned_id[2:].isdigit():
            raise serializers.ValidationError(
                "Mã bác sĩ phải có format BS + số (ví dụ: BS001)"
            )

        return cleaned_id

    @staticmethod
    def validate_years_experience(years: int) -> int:
        if not isinstance(years, int):
            raise serializers.ValidationError("Số năm kinh nghiệm phải là số nguyên")

        if years < MIN_YEARS_EXPERIENCE:
            raise serializers.ValidationError("Số năm kinh nghiệm không được âm")

        if years > MAX_YEARS_EXPERIENCE:
            raise serializers.ValidationError(
                f"Số năm kinh nghiệm không được vượt quá {MAX_YEARS_EXPERIENCE} năm"
            )

        return years


class DoctorValidationMixin:
    """
    Mixin class chứa các validation methods cho Doctor serializers
    """

    def validate_doctor_id(self, value: str) -> str:
        return DoctorValidators.validate_doctor_id(value)

    def validate_years_of_experience(self, value: int) -> int:
        return DoctorValidators.validate_years_experience(value)


class DoctorSerializer(DoctorValidationMixin, serializers.ModelSerializer):
    """
    Serializer cho bác sĩ
    Hiển thị thông tin bác sĩ với user_id để liên kết tài khoản
    """

    title = serializers.ReadOnlyField(help_text="Danh xưng bác sĩ")

    class Meta:
        model = Doctors
        fields = [
            "id",
            "doctor_id",
            "fullname",
            "title",
            "specialization",
            "phone",
            "email",
            "user_id",  # ID của tài khoản User liên kết (nullable)
            "years_of_experience",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "title")


class DoctorListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách bác sĩ"""

    title = serializers.ReadOnlyField()

    class Meta:
        model = Doctors
        fields = [
            "id",
            "doctor_id",
            "fullname",
            "title",
            "specialization",
            "phone",
            "is_active",
        ]


class DoctorDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho bác sĩ"""

    title = (
        serializers.ReadOnlyField()
    )  # chỉ hiển thị data, không cho phép khi input tạo/cập nhật
    user_info = (
        serializers.SerializerMethodField()
    )  # định nghĩa field được tính toán bởi method, hiển thị thông tin user liên kết

    class Meta:  # hứa cấu hình cho serializer (model, fields, validation, etc.), ModelSerializer đều cần Meta class
        model = Doctors  # model đại diện
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_user_info(self, obj: Doctors) -> dict | None:
        """Lấy thông tin user liên kết, tài khoản bác sĩ"""
        if obj.user_id:
            return {
                "username": obj.user_id.username,
                "email": obj.user_id.email,
                "is_active": obj.user_id.is_active,
            }
        return None
