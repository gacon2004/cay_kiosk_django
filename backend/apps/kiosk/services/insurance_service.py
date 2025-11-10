"""
SERVICE LAYER - Insurance Service
Xử lý business logic phức tạp liên quan đến bảo hiểm y tế
"""

from datetime import date, timedelta
from typing import Dict, Optional, Tuple

from apps.kiosk.models import Insurance
from django.core.exceptions import ValidationError
from django.db import transaction


class InsuranceService:
    """
    Service class xử lý business logic cho bảo hiểm y tế
    """

    @staticmethod
    def create_insurance(data: Dict) -> Insurance:
        """
        Tạo bảo hiểm mới với đầy đủ validation

        Args:
            data (dict): Dictionary chứa tất cả thông tin bảo hiểm
                Required fields: citizen_id, insurance_id, fullname, gender,
                                dob, phone_number, registration_place, valid_from, expired

        Returns:
            Insurance: Instance của Insurance vừa tạo

        Raises:
            ValidationError: Nếu dữ liệu không hợp lệ
        """
        # Validate required fields
        required_fields = [
            "citizen_id",
            "insurance_id",
            "fullname",
            "gender",
            "dob",
            "phone_number",
            "registration_place",
            "valid_from",
            "expired",
        ]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Thiếu trường bắt buộc: {field}")

        citizen_id = data["citizen_id"]
        insurance_id = data["insurance_id"]
        fullname = data["fullname"]
        gender = data["gender"]
        dob = data["dob"]
        phone_number = data["phone_number"]
        registration_place = data["registration_place"]
        valid_from = data["valid_from"]
        expired = data["expired"]
        # Validation logic từ model
        if Insurance.objects.filter(insurance_id=insurance_id).exists():
            raise ValidationError(f"Số thẻ BHYT {insurance_id} đã tồn tại")

        if Insurance.objects.filter(citizen_id=citizen_id).exists():
            raise ValidationError(f"CCCD {citizen_id} đã có thẻ bảo hiểm")

        if valid_from >= expired:
            raise ValidationError("Ngày bắt đầu hiệu lực phải nhỏ hơn ngày hết hạn")

        if dob >= date.today():
            raise ValidationError("Ngày sinh phải nhỏ hơn ngày hiện tại")

        # Validate gender
        if gender not in [0, 1]:
            raise ValidationError("Giới tính phải là 0 (Nữ) hoặc 1 (Nam)")

        # Validate citizen_id format (12 digits)
        if not citizen_id.isdigit() or len(citizen_id) != 12:
            raise ValidationError("CCCD phải là 12 chữ số")

        # Validate insurance_id format (10 digits)
        if not insurance_id.isdigit() or len(insurance_id) != 10:
            raise ValidationError("Mã thẻ BHYT phải là 10 chữ số")

        # Tạo insurance
        insurance = Insurance.objects.create(
            citizen_id=citizen_id,
            insurance_id=insurance_id,
            fullname=fullname,
            gender=gender,
            dob=dob,
            phone_number=phone_number,
            registration_place=registration_place,
            valid_from=valid_from,
            expired=expired,
        )
        return insurance

    @staticmethod
    def get_all_insurances():
        """Lấy tất cả bảo hiểm"""
        return Insurance.objects.all()

    @staticmethod
    def check_insurance_validity(insurance: Insurance):
        """
        Kiểm tra tính hợp lệ của thẻ BHYT
        """
        return {
            "insurance_id": insurance.insurance_id,
            "citizen_id": insurance.citizen_id,
            "fullname": insurance.fullname,
            "expired": insurance.expired,
            "is_valid": insurance.is_valid,
            "days_left": insurance.days_until_expiry,
            "status": "Còn hiệu lực" if insurance.is_valid else "Hết hạn",
        }

    @staticmethod
    def get_insurance_by_citizen_id(citizen_id: str):
        """Tìm bảo hiểm theo CCCD"""
        try:
            return Insurance.objects.get(citizen_id=citizen_id)
        except Insurance.DoesNotExist:
            return None

    @staticmethod
    def get_all_valid_insurances():
        """Lấy danh sách thẻ BHYT còn hiệu lực"""
        return Insurance.objects.filter(expired__gte=date.today())

    @staticmethod
    def get_all_expired_insurances():
        """Lấy danh sách thẻ BHYT đã hết hạn"""
        return Insurance.objects.filter(expired__lt=date.today())

    @staticmethod
    def get_expiring_soon(days: int = 30):
        """Lấy danh sách thẻ BHYT sắp hết hạn (trong X ngày tới)"""
        threshold = date.today().replace(day=date.today().day + days)
        return Insurance.objects.filter(
            expired__gte=date.today(), expired__lte=threshold
        )

    @staticmethod
    def update_insurance(insurance: Insurance, data: Dict) -> Insurance:
        """Cập nhật thông tin bảo hiểm"""
        for key, value in data.items():
            setattr(insurance, key, value)
        insurance.save()
        return insurance

    @staticmethod
    def delete_insurance(insurance: Insurance) -> None:
        """Xóa bảo hiểm"""
        insurance.delete()
