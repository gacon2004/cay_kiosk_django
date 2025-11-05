"""
VIEW LAYER (Serializers) - Insurance Serializer
Chuyển đổi Insurance model thành JSON và validate input
"""

from typing import Dict, Any, Optional
from datetime import date
from rest_framework import serializers
from apps.kiosk.models import Insurance, Patients


class InsuranceSerializer(serializers.ModelSerializer):
    """Serializer cho bảo hiểm y tế"""
    is_valid = serializers.ReadOnlyField(help_text="Thẻ còn hiệu lực hay không")
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Insurance
        fields = [
            "insurance_id",
            "citizen_id",
            "fullname",
            "gender",
            "dob",
            "phone_number",
            "registration_place",
            "valid_from",
            "expired",
            "is_valid",
            "days_until_expiry",
        ]

    def get_days_until_expiry(self, obj: Insurance) -> Optional[int]:
        """Số ngày còn lại đến khi hết hạn"""
        return obj.days_until_expiry

    def validate_insurance_id(self, insurance_id: str) -> str:
        """
        Validate số thẻ BHYT
        Args:
            insurance_id: Số thẻ BHYT cần validate
        Returns:
            str: Số thẻ BHYT đã uppercase
        Raises:
            ValidationError: Nếu số thẻ không hợp lệ
        """
        # Số thẻ BHYT thường có format: XX1234567890123 (15 ký tự)
        if len(insurance_id) < 10:
            raise serializers.ValidationError("Số thẻ BHYT không hợp lệ")
        return insurance_id.upper()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ngày hiệu lực và ngày hết hạn"""
        valid_from = data.get("valid_from")
        expired = data.get("expired")

        if expired and expired < date.today():
            raise serializers.ValidationError({"expired": "Ngày hết hạn đã qua"})

        if valid_from and expired and valid_from >= expired:
            raise serializers.ValidationError(
                {"valid_from": "Ngày bắt đầu phải nhỏ hơn ngày hết hạn"}
            )
        return data


class InsuranceListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách bảo hiểm"""
    is_valid = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    
    class Meta:
        model = Insurance
        fields = [
            "insurance_id",
            "citizen_id",
            "fullname",
            "gender",
            "dob",
            "phone_number",
            "registration_place",
            "valid_from",
            "expired",
            "is_valid",
            "days_until_expiry",
        ]
