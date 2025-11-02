"""
SERVICE LAYER - Patient Service
Xử lý business logic phức tạp liên quan đến bệnh nhân
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.users.models import Patients, Insurance


class PatientService:
    """
    Service class xử lý business logic cho bệnh nhân
    Tách biệt business logic khỏi views để dễ test và maintain
    """
    
    @staticmethod
    def create_patient_with_insurance(patient_data, insurance_data=None):
        """
        Tạo bệnh nhân kèm thông tin bảo hiểm trong một transaction
        
        Args:
            patient_data (dict): Thông tin bệnh nhân
            insurance_data (dict): Thông tin bảo hiểm (optional)
        
        Returns:
            tuple: (patient, insurance) hoặc (patient, None)
        """
        with transaction.atomic():
            # Tạo bệnh nhân
            patient = Patients.objects.create(**patient_data)
            
            # Tạo bảo hiểm nếu có
            insurance = None
            if insurance_data:
                insurance_data['patient_id'] = patient
                insurance = Insurance.objects.create(**insurance_data)
            
            return patient, insurance
    
    @staticmethod
    def update_patient_info(patient_id, update_data):
        """
        Cập nhật thông tin bệnh nhân với validation
        
        Args:
            patient_id (int): ID bệnh nhân
            update_data (dict): Dữ liệu cần cập nhật
        
        Returns:
            Patients: Bệnh nhân đã cập nhật
        """
        try:
            patient = Patients.objects.get(id=patient_id)
            
            for key, value in update_data.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)
            
            patient.full_clean()  # Validate
            patient.save()
            
            return patient
        except Patients.DoesNotExist:
            raise ValidationError(f"Không tìm thấy bệnh nhân với ID {patient_id}")
    
    @staticmethod
    def find_patient_by_national_id(national_id):
        """
        Tìm bệnh nhân theo CMND/CCCD
        
        Args:
            national_id (str): Số CMND/CCCD
        
        Returns:
            Patients hoặc None
        """
        try:
            return Patients.objects.get(national_id=national_id)
        except Patients.DoesNotExist:
            return None
    
    @staticmethod
    def get_patients_by_age_range(min_age, max_age):
        """
        Lấy danh sách bệnh nhân theo khoảng tuổi
        
        Args:
            min_age (int): Tuổi tối thiểu
            max_age (int): Tuổi tối đa
        
        Returns:
            QuerySet: Danh sách bệnh nhân
        """
        from datetime import date
        
        today = date.today()
        max_birth_year = today.year - min_age
        min_birth_year = today.year - max_age
        
        return Patients.objects.filter(
            date_of_birth__year__gte=min_birth_year,
            date_of_birth__year__lte=max_birth_year
        )
    
    @staticmethod
    def get_patients_with_valid_insurance():
        """
        Lấy danh sách bệnh nhân có bảo hiểm còn hiệu lực
        
        Returns:
            QuerySet: Danh sách bệnh nhân
        """
        from datetime import date
        
        return Patients.objects.filter(
            insurances__expiry_date__gte=date.today()
        ).distinct()
    
    @staticmethod
    def check_duplicate_national_id(national_id, exclude_id=None):
        """
        Kiểm tra CMND/CCCD có bị trùng không
        
        Args:
            national_id (str): Số CMND/CCCD cần kiểm tra
            exclude_id (int): ID bệnh nhân cần loại trừ (dùng khi update)
        
        Returns:
            bool: True nếu trùng, False nếu không trùng
        """
        query = Patients.objects.filter(national_id=national_id)
        
        if exclude_id:
            query = query.exclude(id=exclude_id)
        
        return query.exists()
