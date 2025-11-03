"""
CONTROLLER LAYER - Doctor Views
Xử lý các request liên quan đến bác sĩ
"""
from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.models import Doctors
from apps.users.serializers import (
    DoctorSerializer,
    DoctorListSerializer,
    DoctorDetailSerializer,
)


class DoctorViewSet(viewsets.ModelViewSet):
    """
    CONTROLLER - Doctor Management ViewSet
    
    Xử lý CRUD operations cho bác sĩ:
    - GET /api/users/doctors/ - Lấy danh sách bác sĩ
    - POST /api/users/doctors/ - Tạo bác sĩ mới
    - GET /api/users/doctors/{id}/ - Xem chi tiết bác sĩ
    - PUT /api/users/doctors/{id}/ - Cập nhật bác sĩ
    - PATCH /api/users/doctors/{id}/ - Cập nhật một phần
    - DELETE /api/users/doctors/{id}/ - Xóa bác sĩ
    
    Custom actions:
    - GET /api/users/doctors/by_specialization/?spec=xxx - Tìm theo chuyên khoa
    - GET /api/users/doctors/active/ - Lấy danh sách bác sĩ đang hoạt động
    - POST /api/users/doctors/{id}/activate/ - Kích hoạt bác sĩ
    - POST /api/users/doctors/{id}/deactivate/ - Vô hiệu hóa bác sĩ
    """
    
    queryset = Doctors.objects.all()
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings
    
    # Filters, Search, Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['doctor_id', 'full_name', 'specialization', 'email']
    filterset_fields = ['specialization', 'is_active']
    ordering_fields = ['created_at', 'full_name', 'years_of_experience']
    ordering = ['full_name']
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp với action"""
        if self.action == 'list':
            return DoctorListSerializer
        elif self.action == 'retrieve':
            return DoctorDetailSerializer
        return DoctorSerializer
    
    def get_permissions(self):
        """Phân quyền - Chỉ admin mới có quyền tạo, sửa, xóa bác sĩ"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'activate', 'deactivate']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def by_specialization(self, request):
        """
        GET /api/users/doctors/by_specialization/?spec=Tim mạch
        Tìm bác sĩ theo chuyên khoa
        """
        specialization = request.query_params.get('spec', None)
        
        if not specialization:
            return Response({
                'error': 'Vui lòng cung cấp tên chuyên khoa (spec)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        doctors = Doctors.objects.filter(
            specialization__icontains=specialization,
            is_active=True
        )
        
        serializer = self.get_serializer(doctors, many=True)
        return Response({
            'specialization': specialization,
            'count': doctors.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        GET /api/users/doctors/active/
        Lấy danh sách bác sĩ đang hoạt động
        """
        active_doctors = Doctors.objects.filter(is_active=True)
        serializer = self.get_serializer(active_doctors, many=True)
        return Response({
            'count': active_doctors.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """
        POST /api/users/doctors/{id}/activate/
        Kích hoạt bác sĩ
        """
        doctor = self.get_object()
        doctor.is_active = True
        doctor.save()
        
        return Response({
            'message': f'Đã kích hoạt bác sĩ {doctor.full_name}',
            'doctor': DoctorSerializer(doctor).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """
        POST /api/users/doctors/{id}/deactivate/
        Vô hiệu hóa bác sĩ
        """
        doctor = self.get_object()
        doctor.is_active = False
        doctor.save()
        
        return Response({
            'message': f'Đã vô hiệu hóa bác sĩ {doctor.full_name}',
            'doctor': DoctorSerializer(doctor).data
        })
    
    @action(detail=False, methods=['get'])
    def specializations(self, request):
        """
        GET /api/users/doctors/specializations/
        Lấy danh sách các chuyên khoa có sẵn
        """
        specializations = Doctors.objects.values_list('specialization', flat=True).distinct()
        
        return Response({
            'count': len(specializations),
            'specializations': list(specializations)
        })
    
    def create(self, request, *args, **kwargs):
        """POST /api/users/doctors/ - Tạo bác sĩ mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'message': 'Thêm bác sĩ mới thành công!',
            'doctor': serializer.data
        }, status=status.HTTP_201_CREATED)
