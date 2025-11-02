"""
CONTROLLER LAYER - Bank Information Views
Xử lý các request liên quan đến thông tin ngân hàng
"""
from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.models import BankInformation
from apps.users.serializers import (
    BankInformationSerializer,
    BankInformationListSerializer,
)


class BankInformationViewSet(viewsets.ModelViewSet):
    """
    CONTROLLER - Bank Information Management ViewSet
    
    Xử lý CRUD operations cho thông tin ngân hàng:
    - GET /api/users/banks/ - Lấy danh sách ngân hàng
    - POST /api/users/banks/ - Tạo thông tin ngân hàng mới
    - GET /api/users/banks/{id}/ - Xem chi tiết
    - PUT /api/users/banks/{id}/ - Cập nhật
    - PATCH /api/users/banks/{id}/ - Cập nhật một phần
    - DELETE /api/users/banks/{id}/ - Xóa
    
    Custom actions:
    - GET /api/users/banks/active/ - Lấy danh sách ngân hàng đang hoạt động
    - GET /api/users/banks/by_bank_name/?name=xxx - Tìm theo tên ngân hàng
    """
    
    queryset = BankInformation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    # Filters, Search, Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['bank_id', 'bank_name', 'account_holder']
    filterset_fields = ['bank_name', 'is_active']
    ordering_fields = ['created_at', 'bank_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp với action"""
        if self.action == 'list':
            return BankInformationListSerializer
        return BankInformationSerializer
    
    def get_permissions(self):
        """Phân quyền - Chỉ admin mới có quyền tạo, sửa, xóa"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        GET /api/users/banks/active/
        Lấy danh sách thông tin ngân hàng đang hoạt động
        """
        active_banks = BankInformation.objects.filter(is_active=True)
        serializer = self.get_serializer(active_banks, many=True)
        return Response({
            'count': active_banks.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_bank_name(self, request):
        """
        GET /api/users/banks/by_bank_name/?name=Vietcombank
        Tìm thông tin ngân hàng theo tên
        """
        bank_name = request.query_params.get('name', None)
        
        if not bank_name:
            return Response({
                'error': 'Vui lòng cung cấp tên ngân hàng (name)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        banks = BankInformation.objects.filter(
            bank_name__icontains=bank_name
        )
        
        serializer = self.get_serializer(banks, many=True)
        return Response({
            'bank_name': bank_name,
            'count': banks.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def bank_list(self, request):
        """
        GET /api/users/banks/bank_list/
        Lấy danh sách tên các ngân hàng
        """
        bank_names = BankInformation.objects.values_list('bank_name', flat=True).distinct()
        
        return Response({
            'count': len(bank_names),
            'banks': list(bank_names)
        })
    
    def create(self, request, *args, **kwargs):
        """POST /api/users/banks/ - Tạo thông tin ngân hàng mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'message': 'Thêm thông tin ngân hàng thành công!',
            'bank': serializer.data
        }, status=status.HTTP_201_CREATED)
