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
    BankInformation,
)

# Alias cho backward compatibility
bank_infomation = BankInformation

__all__ = [
    'Patients',
    'Insurance', 
    'Doctors',
    'BankInformation',
    'bank_infomation',  # deprecated, use BankInformation
]
