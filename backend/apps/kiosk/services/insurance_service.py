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
    def create_insurance(patient_id, insurance_number, expiry_date, **kwargs):
        """
        Tạo bảo hiểm mới với validation
        
        Args:
            patient_id (int): ID bệnh nhân
            insurance_number (str): Số thẻ BHYT
            expiry_date (date): Ngày hết hạn
            **kwargs: Các thông tin khác
        
        Returns:
            Insurance: Bảo hiểm mới tạo
        """
        try:
            patient = Patients.objects.get(id=patient_id)
        except Patients.DoesNotExist:
            raise ValidationError(f"Không tìm thấy bệnh nhân với ID {patient_id}")
        
        # Kiểm tra số thẻ BHYT đã tồn tại chưa
        if Insurance.objects.filter(insurance_number=insurance_number).exists():
            raise ValidationError(f"Số thẻ BHYT {insurance_number} đã tồn tại")
        
        # Tạo bảo hiểm
        insurance = Insurance.objects.create(
            patient_id=patient,
            insurance_number=insurance_number,
            expiry_date=expiry_date,
            **kwargs
        )
        
        return insurance
    
    @staticmethod
    def renew_insurance(insurance_id, new_expiry_date):
        """
        Gia hạn thẻ bảo hiểm
        
        Args:
            insurance_id (int): ID bảo hiểm
            new_expiry_date (date): Ngày hết hạn mới
        
        Returns:
            Insurance: Bảo hiểm đã gia hạn
        """
        try:
            insurance = Insurance.objects.get(id=insurance_id)
        except Insurance.DoesNotExist:
            raise ValidationError(f"Không tìm thấy bảo hiểm với ID {insurance_id}")
        
        if new_expiry_date <= insurance.expiry_date:
            raise ValidationError("Ngày hết hạn mới phải lớn hơn ngày hết hạn hiện tại")
        
        insurance.expiry_date = new_expiry_date
        insurance.save()
        
        return insurance
    
    @staticmethod
    def get_expiring_insurances(days=30):
        """
        Lấy danh sách thẻ BHYT sắp hết hạn
        
        Args:
            days (int): Số ngày (mặc định 30)
        
        Returns:
            QuerySet: Danh sách bảo hiểm sắp hết hạn
        """
        threshold_date = date.today() + timedelta(days=days)
        
        return Insurance.objects.filter(
            expiry_date__gte=date.today(),
            expiry_date__lte=threshold_date
        )
    
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
            insurance = Insurance.objects.get(id=insurance_id)
        except Insurance.DoesNotExist:
            raise ValidationError(f"Không tìm thấy bảo hiểm với ID {insurance_id}")
        
        days_left = insurance.days_until_expiry()
        
        return {
            'insurance_number': insurance.insurance_number,
            'is_valid': insurance.is_valid,
            'expiry_date': insurance.expiry_date,
            'days_left': days_left,
            'status': 'valid' if insurance.is_valid else 'expired',
            'warning': 'Sắp hết hạn' if 0 < days_left <= 30 else None
        }
    
    @staticmethod
    def get_insurance_by_number(insurance_number):
        """
        Tìm bảo hiểm theo số thẻ
        
        Args:
            insurance_number (str): Số thẻ BHYT
        
        Returns:
            Insurance hoặc None
        """
        try:
            return Insurance.objects.get(insurance_number=insurance_number)
        except Insurance.DoesNotExist:
            return None
    
    @staticmethod
    def get_patient_insurances(patient_id):
        """
        Lấy tất cả bảo hiểm của một bệnh nhân
        
        Args:
            patient_id (int): ID bệnh nhân
        
        Returns:
            QuerySet: Danh sách bảo hiểm
        """
        return Insurance.objects.filter(patient_id=patient_id)
    
    @staticmethod
    def send_expiry_notification(insurance_id):
        """
        Gửi thông báo nhắc nhở gia hạn bảo hiểm
        (Placeholder - cần implement email/SMS service)
        
        Args:
            insurance_id (int): ID bảo hiểm
        
        Returns:
            dict: Kết quả gửi thông báo
        """
        try:
            insurance = Insurance.objects.get(id=insurance_id)
        except Insurance.DoesNotExist:
            raise ValidationError(f"Không tìm thấy bảo hiểm với ID {insurance_id}")
        
        # TODO: Implement actual notification logic (email, SMS)
        return {
            'status': 'success',
            'message': f'Đã gửi thông báo gia hạn cho {insurance.patient_id.full_name}',
            'insurance_number': insurance.insurance_number,
            'expiry_date': insurance.expiry_date
        }
