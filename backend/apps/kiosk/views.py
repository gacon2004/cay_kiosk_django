"""
LEGACY FILE - Deprecated
Sử dụng views từ thư mục views/ theo cấu trúc MVC mới
File này chỉ để backward compatibility
"""

# Import từ cấu trúc MVC mới
from .views import (
    UserViewSet,
    PatientViewSet,
    InsuranceViewSet,
    DoctorViewSet,
    ClinicViewSet,
    ServiceExamViewSet
)

__all__ = [
    "UserViewSet",
    "PatientViewSet",
    "InsuranceViewSet",
    "DoctorViewSet",
    "ClinicViewSet",
    "ServiceExamViewSet",
]
