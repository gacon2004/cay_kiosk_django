"""
CONTROLLER LAYER - Clinic ViewSet
Xử lý các HTTP requests liên quan đến phòng khám
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # Import AllowAny permission
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps.users.models import Clinic
from apps.users.serializers import (
    ClinicSerializer,
    ClinicListSerializer,
    ClinicCreateSerializer,
    ClinicUpdateSerializer,
)


@method_decorator(csrf_exempt, name='dispatch')
class ClinicViewSet(viewsets.ModelViewSet):
    """
    ViewSet để quản lý phòng khám
    
    Endpoints:
    - GET /clinics/ - Lấy danh sách phòng khám
    - POST /clinics/ - Tạo phòng khám mới
    - GET /clinics/{id}/ - Lấy chi tiết 1 phòng khám
    - PUT/PATCH /clinics/{id}/ - Cập nhật phòng khám
    - DELETE /clinics/{id}/ - Xóa phòng khám
    - GET /clinics/active/ - Lấy các phòng khám đang hoạt động
    - POST /clinics/{id}/activate/ - Kích hoạt phòng khám
    - POST /clinics/{id}/deactivate/ - Vô hiệu hóa phòng khám
    """
    
    # QuerySet lấy tất cả phòng khám, sắp xếp theo tên
    queryset = Clinic.objects.all().order_by('name')
    # Serializer mặc định
    serializer_class = ClinicSerializer
    # Cho phép truy cập không cần authentication (để test)
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        """
        Override để force AllowAny permission cho tất cả actions
        """
        return [AllowAny()]
    
    def get_serializer_class(self):
        """
        Override method để chọn serializer phù hợp với từng action
        - list: dùng ClinicListSerializer (rút gọn)
        - create: dùng ClinicCreateSerializer (validation tạo mới)
        - update/partial_update: dùng ClinicUpdateSerializer (validation update)
        - còn lại: dùng ClinicSerializer (đầy đủ)
        """
        if self.action == 'list':
            return ClinicListSerializer
        elif self.action == 'create':
            return ClinicCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClinicUpdateSerializer
        return ClinicSerializer
    
    def list(self, request, *args, **kwargs):
        """
        GET /clinics/
        Lấy danh sách tất cả phòng khám
        
        Query params:
        - is_active: filter theo trạng thái (true/false)
        - search: tìm kiếm theo tên phòng
        """
        # Lấy queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter theo trạng thái nếu có
        is_active = request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Search theo tên phòng nếu có
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Serialize data
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """
        POST /clinics/
        Tạo phòng khám mới
        
        Body: {
            "name": "Tên phòng khám",
            "address": "Địa chỉ",
            "is_active": true
        }
        """
        # Validate và serialize data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Lưu vào database
        self.perform_create(serializer)
        
        # Trả về data đầy đủ với ClinicSerializer
        clinic = serializer.instance
        response_serializer = ClinicSerializer(clinic)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /clinics/{id}/
        Lấy chi tiết 1 phòng khám
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        PUT /clinics/{id}/
        Cập nhật toàn bộ thông tin phòng khám
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Validate và serialize data
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # Lưu vào database
        self.perform_update(serializer)
        
        # Trả về data đầy đủ
        response_serializer = ClinicSerializer(instance)
        return Response(response_serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /clinics/{id}/
        Cập nhật một phần thông tin phòng khám
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /clinics/{id}/
        Xóa phòng khám
        """
        instance = self.get_object()
        clinic_name = instance.name
        self.perform_destroy(instance)
        
        return Response(
            {'message': f'Đã xóa phòng khám "{clinic_name}" thành công'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        GET /clinics/active/
        Lấy danh sách các phòng khám đang hoạt động
        """
        # Filter chỉ lấy phòng khám is_active=True
        queryset = self.get_queryset().filter(is_active=True)
        serializer = ClinicListSerializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        POST /clinics/{id}/activate/
        Kích hoạt phòng khám
        """
        # Lấy clinic theo pk
        clinic = self.get_object()
        
        # Kiểm tra đã active chưa
        if clinic.is_active:
            return Response(
                {'message': f'Phòng khám "{clinic.name}" đã ở trạng thái hoạt động'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Kích hoạt phòng khám
        clinic.activate()
        
        # Trả về data đã update
        serializer = ClinicSerializer(clinic)
        return Response({
            'message': f'Đã kích hoạt phòng khám "{clinic.name}" thành công',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        POST /clinics/{id}/deactivate/
        Vô hiệu hóa phòng khám
        """
        # Lấy clinic theo pk
        clinic = self.get_object()
        
        # Kiểm tra đã inactive chưa
        if not clinic.is_active:
            return Response(
                {'message': f'Phòng khám "{clinic.name}" đã ở trạng thái ngừng hoạt động'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vô hiệu hóa phòng khám
        clinic.deactivate()
        
        # Trả về data đã update
        serializer = ClinicSerializer(clinic)
        return Response({
            'message': f'Đã vô hiệu hóa phòng khám "{clinic.name}" thành công',
            'data': serializer.data
        })
