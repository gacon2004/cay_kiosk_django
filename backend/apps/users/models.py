"""
LEGACY FILE - Deprecated
Sử dụng models từ thư mục models/ theo cấu trúc MVC mới
File này chỉ để backward compatibility
"""

# Import từ cấu trúc MVC mới
from .models import (
    Patients,
    Insurance,
    Doctors,
    Clinic
)


__all__ = [
    'Patients',
    'Insurance', 
    'Doctors',
    'Clinic',
]
