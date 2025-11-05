"""
SERVICE LAYER - Insurance Service
Xử lý business logic phức tạp liên quan đến bảo hiểm y tế
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from apps.kiosk.models import Insurance, Patients


class InsuranceService:
    """
    Service class xử lý business logic cho bảo hiểm y tế
    """
    
    @staticmethod
    def create_insurance(citizen_id: str, insurance_id: str, valid_from: date, expired: date, **kwargs):
        """
        Tạo bảo hiểm mới với validation

        Args:
            citizen_id (str): CCCD
            insurance_id (str): Số thẻ BHYT
            valid_from (date): Ngày bắt đầu hiệu lực
            expired (date): Ngày hết hạn
            **kwargs: Các thông tin khác
        """
        if Insurance.objects.filter(insurance_id=insurance_id).exists():
            raise ValidationError(f"Số thẻ BHYT {insurance_id} đã tồn tại")

        if valid_from >= expired:
            raise ValidationError("Ngày bắt đầu hiệu lực phải nhỏ hơn ngày hết hạn")

        insurance = Insurance.objects.create(
            citizen_id=citizen_id,
            insurance_id=insurance_id,
            valid_from=valid_from,
            expired=expired,
            **kwargs
        )
        return insurance
    
    @staticmethod
    def check_insurance_validity(insurance_id):
        """
        Kiểm tra tính hợp lệ của thẻ BHYT
        
        Args:
            insurance_id (int): ID bảo hiểm
        
        Returns:
            dict: Thông tin về tính hợp lệ
        """
        try:
            insurance: Insurance = Insurance.objects.get(insurance_id=insurance_id)
        except Insurance.DoesNotExist:
            raise ValidationError(f"Không tìm thấy bảo hiểm với ID {insurance_id}")

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
    def get_expiring_soon(days: int = 30):
        """Lấy danh sách thẻ BHYT sắp hết hạn (trong X ngày tới)"""
        threshold = date.today().replace(day=date.today().day + days)
        return Insurance.objects.filter(expired__gte=date.today(), expired__lte=threshold)
