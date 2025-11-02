from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

# Nếu có models cũ
try:
    from .models import Patients, Insurance, Doctors, bank_infomation
    from .serializer import PatientSerializer, InsuranceSerializer, DoctorSerializer, BankInformationSerializer
except:
    pass

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint cho Users (CRUD đầy đủ):
    - GET /api/users/ - Lấy danh sách users
    - POST /api/users/ - Tạo user mới (chỉ admin)
    - GET /api/users/{id}/ - Xem chi tiết user
    - PUT /api/users/{id}/ - Cập nhật user (toàn bộ)
    - PATCH /api/users/{id}/ - Cập nhật user (một phần)
    - DELETE /api/users/{id}/ - Xóa user (chỉ admin)
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username', 'email']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        # Trả về serializer đơn giản
        from rest_framework import serializers
        
        class UserSerializer(serializers.ModelSerializer):
            full_name = serializers.SerializerMethodField()
            
            class Meta:
                model = User
                fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                         'full_name', 'is_active', 'is_staff', 'date_joined', 'last_login']
                read_only_fields = ['id', 'date_joined', 'last_login']
            
            def get_full_name(self, obj):
                return f"{obj.first_name} {obj.last_name}".strip()
        
        return UserSerializer
    
    def get_permissions(self):
        """Chỉ admin mới có quyền create, update, delete"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """POST /api/users/{id}/activate/ - Kích hoạt user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({
            'message': f'User {user.username} đã được kích hoạt!'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """POST /api/users/{id}/deactivate/ - Vô hiệu hóa user"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({
            'message': f'User {user.username} đã bị vô hiệu hóa!'
        })
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """GET /api/users/me/ - Lấy thông tin user hiện tại"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """GET /api/users/active/ - Lấy danh sách users đang active"""
        active_users = User.objects.filter(is_active=True)
        serializer = self.get_serializer(active_users, many=True)
        return Response(serializer.data)


# ===== CÁC VIEWSET CŨ (Patients, Insurance, Doctors) =====
# Giữ lại nếu models còn tồn tại

try:
    class PatientViewSet(viewsets.ModelViewSet):
        """
        API endpoint cho Patients:
        - GET /api/users/patients/ - Lấy danh sách
        - POST /api/users/patients/ - Tạo mới
        - GET /api/users/patients/{id}/ - Xem chi tiết
        - PUT/PATCH /api/users/patients/{id}/ - Cập nhật
        - DELETE /api/users/patients/{id}/ - Xóa
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
        - GET /api/users/insurance/ - Lấy danh sách
        - POST /api/users/insurance/ - Tạo mới
        - GET /api/users/insurance/{id}/ - Xem chi tiết
        - PUT/PATCH /api/users/insurance/{id}/ - Cập nhật
        - DELETE /api/users/insurance/{id}/ - Xóa
        """
        queryset = Insurance.objects.all()
        serializer_class = InsuranceSerializer

    class DoctorViewSet(viewsets.ModelViewSet):
        """
        API endpoint cho Doctors:
        - GET /api/users/doctors/ - Lấy danh sách
        - POST /api/users/doctors/ - Tạo mới
        - GET /api/users/doctors/{id}/ - Xem chi tiết
        - PUT/PATCH /api/users/doctors/{id}/ - Cập nhật
        - DELETE /api/users/doctors/{id}/ - Xóa
        """
        queryset = Doctors.objects.all()
        serializer_class = DoctorSerializer
        
except:
    # Models không tồn tại, bỏ qua
    pass


