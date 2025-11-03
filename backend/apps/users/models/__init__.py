"""
MODEL LAYER - Users App Models
Import tất cả models để Django có thể nhận diện
"""
from .patient import Patients
from .insurance import Insurance
from .doctor import Doctors
from .clinic import Clinic  # Import model Clinic mới tạo

__all__ = [
    'Patients',
    'Insurance',
    'Doctors',
    'Clinic',  # Export Clinic để các module khác có thể import
]
