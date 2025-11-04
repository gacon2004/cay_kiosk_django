"""
VIEW LAYER (Serializers) - Doctor Serializer
Chuyển đổi Doctor model thành JSON và validate input
"""

from rest_framework import serializers
from apps.kiosk.models import Doctors


class DoctorSerializer(serializers.ModelSerializer):
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
            "full_name",
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

    def validate_doctor_id(self, doctor_id: str):
        """Validate mã bác sĩ"""
        if not doctor_id.startswith("BS"):
            raise serializers.ValidationError("Mã bác sĩ phải bắt đầu bằng 'BS'")
        return doctor_id.upper()

    def validate_years_of_experience(self, years_of_experience: int):
        """Validate số năm kinh nghiệm"""
        if years_of_experience < 0:
            raise serializers.ValidationError("Số năm kinh nghiệm không được âm")
        if years_of_experience > 60:
            raise serializers.ValidationError("Số năm kinh nghiệm không hợp lệ")
        return years_of_experience


class DoctorListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách bác sĩ"""

    title = serializers.ReadOnlyField()

    class Meta:
        model = Doctors
        fields = [
            "id",
            "doctor_id",
            "full_name",
            "title",
            "specialization",
            "phone",
            "is_active",
        ]


class DoctorDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho bác sĩ"""

    title = serializers.ReadOnlyField()
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Doctors
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_user_info(self, obj: Doctors) -> dict | None:
        """Lấy thông tin user liên kết"""
        if obj.user_id:
            return {
                "username": obj.user_id.username,
                "email": obj.user_id.email,
                "is_active": obj.user_id.is_active,
            }
        return None
