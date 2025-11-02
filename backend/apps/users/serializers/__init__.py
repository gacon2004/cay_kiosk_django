"""
VIEW LAYER (Serializers) - Users App Serializers
Import tất cả serializers
"""
from .patient_serializer import (
    PatientSerializer,
    PatientListSerializer,
    PatientDetailSerializer,
)
from .insurance_serializer import (
    InsuranceSerializer,
    InsuranceListSerializer,
)
from .doctor_serializer import (
    DoctorSerializer,
    DoctorListSerializer,
    DoctorDetailSerializer,
)
from .bank_serializer import (
    BankInformationSerializer,
    BankInformationListSerializer,
)
from .user_serializer import (
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)

__all__ = [
    # Patient
    'PatientSerializer',
    'PatientListSerializer',
    'PatientDetailSerializer',
    # Insurance
    'InsuranceSerializer',
    'InsuranceListSerializer',
    # Doctor
    'DoctorSerializer',
    'DoctorListSerializer',
    'DoctorDetailSerializer',
    # Bank
    'BankInformationSerializer',
    'BankInformationListSerializer',
    # User
    'UserSerializer',
    'UserListSerializer',
    'UserCreateSerializer',
    'UserUpdateSerializer',
]
