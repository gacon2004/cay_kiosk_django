"""
LEGACY FILE - Deprecated
Sử dụng models từ thư mục models/ theo cấu trúc MVC mới
File này chỉ để backward compatibility
"""

# Import từ cấu trúc MVC mới
from .models import (
    ServiceExam,
    Patients,
    Insurance,
    Doctors,
    Clinic
)


__all__ = [
    'ServiceExam',
    'Patients',
    'Insurance', 
    'Doctors',
    'Clinic',
]
