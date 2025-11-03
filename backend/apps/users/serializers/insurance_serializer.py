"""
VIEW LAYER (Serializers) - Insurance Serializer
Chuyển đổi Insurance model thành JSON và validate input
"""

from rest_framework import serializers
from apps.users.models import Insurance, Patients


class InsuranceSerializer(serializers.ModelSerializer):
    """Serializer cho bảo hiểm y tế"""

    # Hiển thị thông tin bệnh nhân khi đọc
    patient = serializers.SerializerMethodField(read_only=True)

    # Chấp nhận patient_id khi ghi
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patients.objects.all(), write_only=True
    )

    is_valid = serializers.ReadOnlyField(help_text="Thẻ còn hiệu lực hay không")
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Insurance
        fields = [
            "id",
            "patient",
            "patient_id",
            "insurance_number",
            "expiry_date",
            "issued_date",
            "insurance_type",
            "is_valid",
            "days_until_expiry",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def get_patient(self, obj):
        """Lấy thông tin bệnh nhân"""
        return {
            "id": obj.patient_id.id,
            "full_name": obj.patient_id.full_name,
            "national_id": obj.patient_id.national_id,
        }

    def get_days_until_expiry(self, obj):
        """Số ngày còn lại đến khi hết hạn"""
        return obj.days_until_expiry()

    def validate_insurance_number(self, value):
        """Validate số thẻ BHYT"""
        # Số thẻ BHYT thường có format: XX1234567890123 (15 ký tự)
        if len(value) < 10:
            raise serializers.ValidationError("Số thẻ BHYT không hợp lệ")
        return value.upper()

    def validate(self, data):
        """Validate expiry_date và issued_date"""
        from datetime import date

        if "expiry_date" in data and data["expiry_date"] < date.today():
            raise serializers.ValidationError({"expiry_date": "Ngày hết hạn đã qua"})

        if "issued_date" in data and "expiry_date" in data:
            if data["issued_date"] >= data["expiry_date"]:
                raise serializers.ValidationError(
                    {"issued_date": "Ngày cấp phải nhỏ hơn ngày hết hạn"}
                )

        return data


class InsuranceListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách bảo hiểm"""

    patient_name = serializers.CharField(source="patient_id.full_name", read_only=True)
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Insurance
        fields = ["id", "insurance_number", "patient_name", "expiry_date", "is_valid"]
