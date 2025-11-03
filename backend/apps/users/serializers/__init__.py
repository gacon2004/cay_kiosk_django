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
from .user_serializer import (
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
# Import các serializers cho Clinic
from .clinic_serializer import (
    ClinicSerializer,
    ClinicListSerializer,
    ClinicCreateSerializer,
    ClinicUpdateSerializer,
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
    # User
    'UserSerializer',
    'UserListSerializer',
    'UserCreateSerializer',
    'UserUpdateSerializer',
    # Clinic
    'ClinicSerializer',
    'ClinicListSerializer',
    'ClinicCreateSerializer',
    'ClinicUpdateSerializer',
]
