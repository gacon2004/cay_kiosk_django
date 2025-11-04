"""
LEGACY FILE - Deprecated
Sử dụng serializers từ thư mục serializers/ theo cấu trúc MVC mới
File này chỉ để backward compatibility
"""
# IDE (VS Code, PyCharm) đọc __all__ để hiển thị gợi ý import.

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
    ClinicCreateSerializer,
    ClinicListSerializer,
    ClinicUpdateSerializer,
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ServiceExamsCreateSerializer,
    ServiceExamsListSerializer,
    ServiceExamsDetailSerializer,
    ServiceExamsUpdateSerializer
    
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
    'ClinicCreateSerializer',
    'ClinicListSerializer',
    'ClinicUpdateSerializer',
    'UserSerializer',
    'UserListSerializer',
    'UserCreateSerializer',
    'UserUpdateSerializer',
    'ServiceExamsCreateSerializer',
    'ServiceExamsListSerializer',
    'ServiceExamsDetailSerializer',
    'ServiceExamsUpdateSerializer',
]
