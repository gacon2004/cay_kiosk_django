"""
CONTROLLER LAYER - Patient Views
Xử lý các request liên quan đến bệnh nhân
"""
from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from apps.kiosk.serializers.insurance_serializer import InsuranceSerializer
from apps.kiosk.models import Patients
from apps.kiosk.serializers import (
    PatientSerializer,
    PatientListSerializer,
    PatientDetailSerializer,
)


class PatientViewSet(viewsets.ModelViewSet):
    """
    CONTROLLER - Patient Management ViewSet
    
    Xử lý CRUD operations cho bệnh nhân:
    - GET /api/patients/ - Lấy danh sách bệnh nhân
    - POST /api/patients/ - Tạo bệnh nhân mới
    - GET /api/patients/{id}/ - Xem chi tiết bệnh nhân
    - PUT /api/patients/{id}/ - Cập nhật bệnh nhân
    - PATCH /api/patients/{id}/ - Cập nhật một phần
    - DELETE /api/patients/{id}/ - Xóa bệnh nhân
    
    Custom actions:
    - GET /api/patients/with_insurance/ - Lấy danh sách bệnh nhân có BHYT
    - GET /api/patients/search_by_national_id/?national_id=xxx - Tìm theo CMND
    """
    
    queryset = Patients.objects.all()
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings
    
    # Filters, Search, Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['national_id', 'full_name', 'phone']
    filterset_fields = ['gender', 'city', 'district', 'ethnicity']
    ordering_fields = ['created_at', 'full_name', 'date_of_birth']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp với action"""
        if self.action == 'list':
            return PatientListSerializer
        elif self.action == 'retrieve':
            return PatientDetailSerializer
        return PatientSerializer
    
    @action(detail=False, methods=['get'])
    def with_insurance(self, request):
        """
        GET /api/patients/with_insurance/
        Lấy danh sách bệnh nhân có bảo hiểm
        """
        patients = Patients.objects.filter(insurances__isnull=False).distinct()
        serializer = self.get_serializer(patients, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search_by_national_id(self, request):
        """
        GET /api/patients/search_by_national_id/?national_id=xxx
        Tìm bệnh nhân theo CMND/CCCD
        """
        national_id = request.query_params.get('national_id', None)
        
        if not national_id:
            return Response({
                'error': 'Vui lòng cung cấp số CMND/CCCD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patients.objects.get(national_id=national_id)
            serializer = PatientDetailSerializer(patient)
            return Response(serializer.data)
        except Patients.DoesNotExist:
            return Response({
                'error': 'Không tìm thấy bệnh nhân với CMND/CCCD này'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def insurances(self, request, pk=None):
        """
        GET /api/patients/{id}/insurances/
        Lấy danh sách bảo hiểm của bệnh nhân
        """
        patient = self.get_object()
        
        insurances = patient.insurances.all()
        serializer = InsuranceSerializer(insurances, many=True)
        
        return Response({
            'patient_id': patient.id,
            'patient_name': patient.full_name,
            'insurances': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """POST /api/patients/ - Tạo bệnh nhân mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'message': 'Tạo hồ sơ bệnh nhân thành công!',
            'patient': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """PUT /api/patients/{id}/ - Cập nhật bệnh nhân"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Cập nhật hồ sơ bệnh nhân thành công!',
            'patient': serializer.data
        })
