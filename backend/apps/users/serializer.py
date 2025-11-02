"""
LEGACY FILE - Deprecated
Sử dụng serializers từ thư mục serializers/ theo cấu trúc MVC mới
File này chỉ để backward compatibility
"""

# Import từ cấu trúc MVC mới
from .serializers import (
    PatientSerializer,
    PatientListSerializer,
    PatientDetailSerializer,
    InsuranceSerializer,
    InsuranceListSerializer,
    DoctorSerializer,
    DoctorListSerializer,
    DoctorDetailSerializer,
    BankInformationSerializer,
    BankInformationListSerializer,
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)

__all__ = [
    'PatientSerializer',
    'PatientListSerializer',
    'PatientDetailSerializer',
    'InsuranceSerializer',
    'InsuranceListSerializer',
    'DoctorSerializer',
    'DoctorListSerializer',
    'DoctorDetailSerializer',
    'BankInformationSerializer',
    'BankInformationListSerializer',
    'UserSerializer',
    'UserListSerializer',
    'UserCreateSerializer',
    'UserUpdateSerializer',
]
