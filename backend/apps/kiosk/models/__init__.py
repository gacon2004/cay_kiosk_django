"""
MODEL LAYER - Kiosk App Models
Import tất cả models để Django có thể nhận diện
"""
# ⚠️ QUAN TRỌNG: Import CustomUser TRƯỚC để tránh circular import
from .user import CustomUser, Users

# Import các models khác sau
from .patient import Patients
from .insurance import Insurance
from .service_exams import ServiceExam
from .doctor import Doctors
from .clinic import Clinic

__all__ = [
    'Patients',
    'Insurance',
    'Doctors',
    'ServiceExam',
    'Clinic',
    'CustomUser',  # Export CustomUser
    'Users',       # Alias cũ (backward compatible)
]
