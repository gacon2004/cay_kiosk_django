"""
CONTROLLER LAYER - User Views
Xử lý các request liên quan đến User
"""
from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from apps.kiosk.serializers import (
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    CONTROLLER - User Management ViewSet
    
    Xử lý CRUD operations cho User:
    - GET /api/users/ - Lấy danh sách users
    - POST /api/users/ - Tạo user mới (chỉ admin)
    - GET /api/users/{id}/ - Xem chi tiết user
    - PUT /api/users/{id}/ - Cập nhật user (toàn bộ)
    - PATCH /api/users/{id}/ - Cập nhật user (một phần)
    - DELETE /api/users/{id}/ - Xóa user (chỉ admin)
    
    Custom actions:
    - GET /api/users/me/ - Lấy thông tin user hiện tại
    - GET /api/users/active/ - Lấy danh sách users active
    - POST /api/users/{id}/activate/ - Kích hoạt user
    - POST /api/users/{id}/deactivate/ - Vô hiệu hóa user
    """
    
    queryset = User.objects.all()
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings
    
    # Filters, Search, Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['is_active', 'is_staff']
    ordering_fields = ['date_joined', 'username', 'email']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp với action"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Override method get_permissions() để customize permission cho từng action

        Ví dụ phân quyền thực tế (UNCOMMENT khi production):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]  # Chỉ admin mới được tạo/sửa/xóa
        elif self.action in ['activate', 'deactivate']:
            return [IsAdminUser()]  # Chỉ admin mới activate/deactivate
        return [IsAuthenticated()]  # Các action khác cần đăng nhập

        Returns:
            list: Danh sách permission instances
        """
        # Tạm thời return AllowAny() cho tất cả actions (để test)
        return [AllowAny()]
    
    # def get_permissions(self):
    #     """Phân quyền theo action"""
    #     if self.action in ['create', 'update', 'partial_update', 'destroy', 'activate', 'deactivate']:
    #         return [permissions.IsAdminUser()]
    #     return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        GET /api/users/me/
        Lấy thông tin user hiện tại
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        GET /api/users/active/
        Lấy danh sách users đang active
        """
        active_users = User.objects.filter(is_active=True)
        serializer = self.get_serializer(active_users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """
        POST /api/users/{id}/activate/
        Kích hoạt user
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({
            'message': f'User {user.username} đã được kích hoạt!',
            'user': UserSerializer(user).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """
        POST /api/users/{id}/deactivate/
        Vô hiệu hóa user
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response({
            'message': f'User {user.username} đã bị vô hiệu hóa!',
            'user': UserSerializer(user).data
        })
    
    def destroy(self, request, *args, **kwargs):
        """DELETE /api/users/{id}/ - Xóa user (soft delete)"""
        user = self.get_object()
        
        # Không cho phép xóa chính mình
        if user == request.user:
            return Response({
                'error': 'Không thể xóa chính mình!'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Không cho phép xóa superuser
        if user.is_superuser:
            return Response({
                'error': 'Không thể xóa superuser!'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Soft delete - chỉ set is_active = False
        user.is_active = False
        user.save()
        
        return Response({
            'message': f'Đã vô hiệu hóa user {user.username}'
        }, status=status.HTTP_204_NO_CONTENT)
