from rest_framework import viewsets
from rest_framework.response import Response
from .models import Patients, Insurance, Doctors, bank_infomation
from .serializer import PatientSerializer, InsuranceSerializer, DoctorSerializer, BankInformationSerializer
from rest_framework.decorators import action
# Create your views here.

class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint cho Patients:
    - GET /api_users/patients/ - Lấy danh sách
    - POST /api_users/patients/ - Tạo mới
    - GET /api_users/patients/{id}/ - Xem chi tiết
    - PUT/PATCH /api_users/patients/{id}/ - Cập nhật
    - DELETE /api_users/patients/{id}/ - Xóa
    """
    queryset = Patients.objects.all()
    serializer_class = PatientSerializer

    @action(detail=False, methods=['get'])
    def with_insurance(self, request):
        patients = Patients.objects.filter(insurance__isnull=False).distinct()
        serializer = self.get_serializer(patients, many=True)
        return Response(serializer.data)

class InsuranceViewSet(viewsets.ModelViewSet):
    """
    API endpoint cho Insurance:
    - GET /api_users/Insurance/ - Lấy danh sách
    - POST /api_users/Insurance/ - Tạo mới
    - GET /api_users/Insurance/{id}/ - Xem chi tiết
    - PUT/PATCH /api_users/Insurance/{id}/ - Cập nhật
    - DELETE /api_users/Insurance/{id}/ - Xóa
    """
    queryset = Insurance.objects.all()
    serializer_class = InsuranceSerializer

class DoctorViewSet(viewsets.ModelViewSet):
    """
    API endpoint cho Insurance:
    - GET /api_users/Doctors/ - Lanh ấy dsách
    - POST /api_users/Doctors/ - Tạo mới
    - GET /api_users/Doctors/{id}/ - Xem chi tiết
    - PUT/PATCH /api_users/Doctors/{id}/ - Cập nhật
    - DELETE /api_users/Doctors/{id}/ - Xóa
    """
    queryset = Doctors.objects.all()
    serializer_class = DoctorSerializer


