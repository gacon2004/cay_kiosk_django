from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response
from apps.kiosk.models import ServiceExam
from rest_framework.permissions import AllowAny
from apps.kiosk.serializers import ServiceExamsListSerializer

class ServiceExamViewSet(viewsets.ModelViewSet):
    """
    CONTROLLER - Service Exam Management ViewSet
    
    Xử lý CRUD operations cho dịch vụ khám:
    - GET /api/kiosk/service_exams/ - Lấy danh sách dịch vụ khám
    - POST /api/kiosk/service_exams/ - Tạo dịch vụ khám mới
    - GET /api/kiosk/service_exams/{id}/ - Xem chi tiết dịch vụ khám
    - PUT /api/kiosk/service_exams/{id}/ - Cập nhật dịch vụ khám
    - PATCH /api/kiosk/service_exams/{id}/ - Cập nhật một phần
    - DELETE /api/kiosk/service_exams/{id}/ - Xóa dịch vụ khám
    """
    queryset = ServiceExam.objects.all().order_by('id')
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings
    
    def get_serializer_class(self):
        if(self.action == 'list'):
            return ServiceExamsListSerializer
    
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
    
    
    