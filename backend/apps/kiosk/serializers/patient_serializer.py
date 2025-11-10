"""
VIEW LAYER (Serializers) - Patient Serializer
Chuyển đổi Patient model thành JSON và validate input
"""

from datetime import date

from apps.kiosk.models import Patients
from rest_framework import serializers


class PatientSerializer(serializers.ModelSerializer):
    """Serializer cho bệnh nhân"""

    age = serializers.ReadOnlyField(help_text="Tuổi tính tự động")

    class Meta:
        model = Patients
        fields = [
            "citizen_id",
            "fullname",
            "dob",
            "age",
            "gender",
            "phone_number",
            "address",
            "occupation",
            "is_insurance",
            "ethnicity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at", "age")

    def validate_citizen_id(self, citizen_id: str) -> str:
        """Validate số CCCD"""
        if not citizen_id.isdigit():
            raise serializers.ValidationError("CCCD phải là số")
        if len(citizen_id) not in [9, 12]:
            raise serializers.ValidationError("CCCD phải 12 số")
        return citizen_id

    def validate_dob(self, dob: date) -> date:
        """Validate ngày sinh"""
        if dob > date.today():
            raise serializers.ValidationError(
                "Ngày sinh không thể lớn hơn ngày hiện tại"
            )

        age = date.today().year - dob.year
        if age > 150:
            raise serializers.ValidationError("Tuổi không hợp lệ")

        return dob


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách bệnh nhân"""

    age = serializers.ReadOnlyField()

    class Meta:
        model = Patients
        fields = [
            "citizen_id",
            "fullname",
            "dob",
            "age",
            "address",
            "gender",
            "phone_number",
            "is_insurance",
            "ethnicity",
            "occupation",
        ]
        read_only_fields = ("citizen_id", "age")


class PatientDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho bệnh nhân (bao gồm insurance)"""

    age = serializers.ReadOnlyField()

    class Meta:
        model = Patients
        fields = "__all__"
        read_only_fields = ("citizen_id", "created_at", "updated_at", "age")
