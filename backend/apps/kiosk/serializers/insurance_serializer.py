"""
VIEW LAYER (Serializers) - Insurance Serializer
Chuyển đổi Insurance model thành JSON và validate input
"""

from datetime import date
from typing import Any, Dict, Optional

from apps.kiosk.models import Insurance, Patients
from rest_framework import serializers


class InsuranceSerializer(serializers.ModelSerializer):
    """Serializer cho bảo hiểm y tế"""

    # FIX: Định dạng ngày tháng cho HTML input type="date" (yyyy-mm-dd)
    dob = serializers.DateField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    )
    valid_from = serializers.DateField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    )
    expired = serializers.DateField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    )

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

    def validate_citizen_id(self, citizen_id: str) -> str:
        """Validate CCCD"""
        if len(citizen_id) != 12:
            raise serializers.ValidationError("Số CCCD phải có đúng 12 số")
        if not citizen_id.isdigit():
            raise serializers.ValidationError("Số CCCD chỉ chứa số")
        return citizen_id

    def validate_phone_number(self, phone_number: str) -> str:
        """Validate số điện thoại"""
        # Loại bỏ khoảng trắng và dấu gạch ngang
        phone_number = phone_number.replace(" ", "").replace("-", "")

        if not phone_number.isdigit():
            raise serializers.ValidationError("Số điện thoại chỉ chứa số")

        if len(phone_number) != 10:
            raise serializers.ValidationError("Số điện thoại phải có 10 số")

        return phone_number

    def validate_insurance_id(self, insurance_id: str) -> str:
        # Số thẻ BHYT thường có format: XX1234567890123 (15 ký tự)
        if len(insurance_id) < 10:
            raise serializers.ValidationError("Số thẻ BHYT không hợp lệ")
        return insurance_id.upper()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ngày hiệu lực và ngày hết hạn"""
        valid_from = data.get("valid_from")
        expired = data.get("expired")
        dob = data.get("dob")

        # Kiểm tra ngày sinh
        if dob and dob > date.today():
            raise serializers.ValidationError(
                {"dob": "Ngày sinh không được lớn hơn ngày hiện tại"}
            )

        # Kiểm tra ngày hết hạn
        if expired and expired < date.today():
            raise serializers.ValidationError({"expired": "Ngày hết hạn đã qua"})

        # Kiểm tra valid_from < expired
        if valid_from and expired and valid_from >= expired:
            raise serializers.ValidationError(
                {"valid_from": "Ngày bắt đầu phải nhỏ hơn ngày hết hạn"}
            )

        return data


class InsuranceCheckSerializer(serializers.Serializer):
    """Serializer cho việc kiểm tra bảo hiểm"""

    citizen_id = serializers.CharField(max_length=12, help_text="Số CCCD cần kiểm tra")

    def validate_citizen_id(self, citizen_id: str) -> str:
        """Validate CCCD"""
        if len(citizen_id) != 12:
            raise serializers.ValidationError("Số CCCD phải có đúng 12 số")
        if not citizen_id.isdigit():
            raise serializers.ValidationError("Số CCCD chỉ chứa số")
        return citizen_id


class InsuranceListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách bảo hiểm"""

    days_until_expiry = serializers.ReadOnlyField()
    dob = serializers.DateField(format="%d/%m/%Y")
    valid_from = serializers.DateField(format="%d/%m/%Y")
    expired = serializers.DateField(format="%d/%m/%Y")

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
