"""
CONTROLLER LAYER - Users App Views
Import tất cả views để Django có thể nhận diện
"""
from .user_view import UserViewSet
from .patient_view import PatientViewSet
from .insurance_view import InsuranceViewSet
from .doctor_view import DoctorViewSet
from .clinic_view import ClinicViewSet  # Import ViewSet cho Clinic
from .service_exam_view import ServiceExamViewSet  # Import ViewSet cho ServiceExam

__all__ = [
    'UserViewSet',
    'PatientViewSet',
    'InsuranceViewSet',
    'DoctorViewSet',
    'ClinicViewSet',  # Export ClinicViewSet
    'ServiceExamViewSet',
]
