"""
CONTROLLER LAYER - Users App Views
Import tất cả views để Django có thể nhận diện
"""
from .user_view import UserViewSet
from .patient_view import PatientViewSet
from .insurance_view import InsuranceViewSet
from .doctor_view import DoctorViewSet
from .bank_view import BankInformationViewSet

__all__ = [
    'UserViewSet',
    'PatientViewSet',
    'InsuranceViewSet',
    'DoctorViewSet',
    'BankInformationViewSet',
]
