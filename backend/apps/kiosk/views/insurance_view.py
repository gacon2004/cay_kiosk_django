"""
CONTROLLER LAYER - Insurance Views
Xử lý các request liên quan đến bảo hiểm y tế
"""
from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from datetime import date, timedelta

from apps.kiosk.models import Insurance
from apps.kiosk.serializers import (
    InsuranceSerializer,
    InsuranceListSerializer,
)


class InsuranceViewSet(viewsets.ModelViewSet):
    """
    CONTROLLER - Insurance Management ViewSet
    
    Xử lý CRUD operations cho bảo hiểm y tế:
    - GET /api/insurance/ - Lấy danh sách bảo hiểm
    - POST /api/insurance/ - Tạo bảo hiểm mới
    - GET /api/insurance/{id}/ - Xem chi tiết
    - PUT /api/insurance/{id}/ - Cập nhật
    - PATCH /api/insurance/{id}/ - Cập nhật một phần
    - DELETE /api/insurance/{id}/ - Xóa
    
    Custom actions:
    - GET /api/insurance/valid/ - Lấy thẻ còn hiệu lực
    - GET /api/insurance/expired/ - Lấy thẻ hết hạn
    - GET /api/insurance/expiring_soon/ - Lấy thẻ sắp hết hạn (30 ngày)
    """
    
    queryset = Insurance.objects.all()
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings
    
    # Filters, Search, Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['insurance_id', 'citizen_id', 'fullname']
    filterset_fields = ['insurance_id', 'citizen_id']
    ordering_fields = ['valid_from','expired']
    ordering = ['-valid_from']
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp với action"""
        if self.action == 'list':
            return InsuranceListSerializer
        return InsuranceSerializer
    
    @action(detail=False, methods=['get'])
    def valid(self, request):
        """
        GET /api/insurance/valid/
        Lấy danh sách thẻ BHYT còn hiệu lực
        """
        valid_insurances = Insurance.objects.filter(expired__gte=date.today())
        serializer = self.get_serializer(valid_insurances, many=True)
        return Response({
            'count': valid_insurances.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """
        GET /api/insurance/expired/
        Lấy danh sách thẻ BHYT đã hết hạn
        """
        expired_insurances = Insurance.objects.filter(expired__lt=date.today())
        serializer = self.get_serializer(expired_insurances, many=True)
        return Response({
            'count': expired_insurances.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """
        GET /api/insurance/expiring_soon/?days=30
        Lấy danh sách thẻ BHYT sắp hết hạn (mặc định 30 ngày)
        """
        days = int(request.query_params.get('days', 30))
        threshold_date = date.today() + timedelta(days=days)
        
        expiring_insurances = Insurance.objects.filter(
            expired__gte=date.today(),
            expired__lte=threshold_date
        )
        
        serializer = self.get_serializer(expiring_insurances, many=True)
        return Response({
            'count': expiring_insurances.count(),
            'message': f'Danh sách thẻ BHYT sắp hết hạn trong {days} ngày tới',
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def check_validity(self, request, pk=None):
        """
        GET /api/insurance/{id}/check_validity/
        Kiểm tra tính hợp lệ của thẻ BHYT
        """
        insurance: Insurance = self.get_object()
        
        return Response({
            'insurance_id': insurance.insurance_id,
            'fullname': insurance.fullname,
            'expired': insurance.expired,
            'is_valid': insurance.is_valid,
            'days_until_expiry': insurance.days_until_expiry(),
            'status': 'Còn hiệu lực' if insurance.is_valid else 'Hết hiệu lực'
        })
    
    def create(self, request, *args, **kwargs):
        """POST /api/insurance/ - Tạo bảo hiểm mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'message': 'Thêm thẻ bảo hiểm thành công!',
            'insurance': serializer.data
        }, status=status.HTTP_201_CREATED)
