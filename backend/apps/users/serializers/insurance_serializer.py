"""
VIEW LAYER (Serializers) - Insurance Serializer
Chuyển đổi Insurance model thành JSON và validate input
"""

from typing import Dict, Any, Optional
from datetime import date
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

    def get_patient(self, obj: Insurance) -> Dict[str, Any]:
        """
        Lấy thông tin bệnh nhân (SerializerMethodField)
        
        Args:
            obj: Insurance instance
        
        Returns:
            Dict[str, Any]: Thông tin bệnh nhân
                {
                    "id": int,
                    "full_name": str,
                    "national_id": str
                }
        """
        return {
            "id": obj.patient_id.id,
            "full_name": obj.patient_id.full_name,
            "national_id": obj.patient_id.national_id,
        }

    def get_days_until_expiry(self, obj: Insurance) -> Optional[int]:
        """
        Số ngày còn lại đến khi hết hạn (SerializerMethodField)
        
        Args:
            obj: Insurance instance
        
        Returns:
            Optional[int]: Số ngày còn lại, hoặc None nếu đã hết hạn
        """
        return obj.days_until_expiry()

    def validate_insurance_number(self, insurance_number: str) -> str:
        """
        Validate số thẻ BHYT
        Args:
            insurance_number: Số thẻ BHYT cần validate
        Returns:
            str: Số thẻ BHYT đã uppercase
        Raises:
            ValidationError: Nếu số thẻ không hợp lệ
        """
        # Số thẻ BHYT thường có format: XX1234567890123 (15 ký tự)
        if len(insurance_number) < 10:
            raise serializers.ValidationError("Số thẻ BHYT không hợp lệ")
        return insurance_number.upper()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate expiry_date và issued_date
        Args:
            data: Dictionary chứa data cần validate
                {
                    "expiry_date": date (optional),
                    "issued_date": date (optional),
                    ...
                }
        Returns:
            Dict[str, Any]: Data đã validate
        Raises:
            ValidationError: Nếu dữ liệu không hợp lệ
        """
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
