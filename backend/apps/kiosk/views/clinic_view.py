"""
CONTROLLER LAYER - Clinic ViewSet
Xử lý các HTTP requests liên quan đến phòng khám

TRÁCH NHIỆM:
- Nhận HTTP Request (GET, POST, PUT, DELETE...)
- Validate input data (dùng Serializer)
- GỌI Service Layer để xử lý business logic
- Trả về HTTP Response (JSON)

KHÔNG LÀM:
- Business logic (để trong Service)
- Direct database queries (để trong Service)
- Complex validation (để trong Service)
"""
import logging
from typing import Any
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError

from apps.kiosk.models import Clinic
from apps.kiosk.serializers import (
    ClinicSerializer,
    ClinicListSerializer,
    ClinicCreateSerializer,
    ClinicUpdateSerializer,
)
from apps.kiosk.services import ClinicService


class ClinicViewSet(viewsets.ModelViewSet):
    """
    CONTROLLER - Clinic Management ViewSet
    Kế thừa từ ModelViewSet → Tự động có các actions:
    - list()    : GET    /clinics/           → Danh sách
    - create()  : POST   /clinics/           → Tạo mới
    - retrieve(): GET    /clinics/{id}/      → Chi tiết
    - update()  : PUT    /clinics/{id}/      → Update toàn bộ
    - partial_update(): PATCH /clinics/{id}/ → Update một phần
    - destroy() : DELETE /clinics/{id}/      → Xóa

    Custom actions (@action decorator):
    - active()     : GET  /clinics/active/        → Lấy clinics đang hoạt động
    - activate()   : POST /clinics/{id}/activate/ → Kích hoạt clinic
    - deactivate() : POST /clinics/{id}/deactivate/ → Vô hiệu hóa clinic

    Tham khảo:
    - ModelViewSet: https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset
    - Actions: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
    """

    # queryset: QuerySet mặc định cho ViewSet
    # DRF sẽ dùng queryset này để lấy data cho các CRUD operations
    queryset = Clinic.objects.all().order_by("name")

    # permission_classes: Danh sách permission classes
    # AllowAny = Cho phép tất cả (không cần authentication)
    # CẢNH BÁO: Chỉ dùng AllowAny trong development/testing!
    # Production nên dùng: IsAuthenticated, IsAdminUser, hoặc custom permission
    permission_classes = [AllowAny]

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

    def get_serializer_class(self):
        """
        Override method để chọn Serializer phù hợp với từng action
        Lý do: Mỗi action có yêu cầu data khác nhau
        - list: Không cần đầy đủ fields → dùng ClinicListSerializer (nhẹ hơn)
        - create: Cần validate khi tạo mới → dùng ClinicCreateSerializer
        - update/partial_update: Cần validate khi update → dùng ClinicUpdateSerializer
        - retrieve: Cần đầy đủ thông tin → dùng ClinicSerializer
        Returns:
            Serializer class: Class serializer tương ứng với action
        """
        if self.action == "list":
            # List: Trả về rút gọn (không cần created_at, updated_at...)
            return ClinicListSerializer
        elif self.action == "create":
            # Create: Validate các trường bắt buộc khi tạo mới
            return ClinicCreateSerializer
        elif self.action in ["update", "partial_update"]:
            # Update: Validate khi cập nhật (cho phép partial)
            return ClinicUpdateSerializer
        # Default: Trả về đầy đủ thông tin
        return ClinicSerializer

    def list(self, request, *args, **kwargs):
        """
        GET /clinics/
        Lấy danh sách tất cả phòng khám

        Query params:
        - is_active: filter theo trạng thái (true/false)
        - search: tìm kiếm theo tên phòng
        """
        # Parse query params
        is_active_param = request.query_params.get("is_active", None)
        is_active = None
        if is_active_param is not None:
            is_active = is_active_param.lower() == "true"

        search = request.query_params.get("search", None)

        # GỌI SERVICE LAYER để lấy data
        queryset = ClinicService.get_all_clinics(is_active=is_active, search=search)

        # Serialize data
        # Type hint giúp IDE biết serializer type
        serializer: ClinicListSerializer = self.get_serializer(queryset, many=True)

        return Response({"count": queryset.count(), "results": serializer.data})

    def create(self, request: dict[str, Any], *args, **kwargs):
        """
        POST /clinics/
        Tạo phòng khám mới
        Body: {
            "name": "Tên phòng khám",
            "address": "Địa chỉ",
            "is_active": true
        }
        """
        # Validate request data với serializer
        # Type hint giúp IDE autocomplete validated_data, errors, data...
        serializer: ClinicCreateSerializer = self.get_serializer(data=request.data)
        logging.info(f"Clinic create request data: {request.data}")
        serializer.is_valid(raise_exception=True)

        try:
            # GỌI SERVICE LAYER để tạo clinic
            clinic = ClinicService.create_clinic(serializer.validated_data)
            # Trả về data đầy đủ
            response_serializer = ClinicSerializer(clinic)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request: dict[str, Any], *args, **kwargs):
        """
        GET /clinics/{id}/
        Lấy chi tiết 1 phòng khám
        """
        try:
            # GỌI SERVICE LAYER để lấy clinic
            clinic = ClinicService.get_clinic_by_id(self.kwargs["pk"])
            # Type hint giúp IDE autocomplete
            serializer: ClinicSerializer = self.get_serializer(clinic)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        PUT /clinics/{id}/
        Cập nhật toàn bộ thông tin phòng khám
        """
        partial = kwargs.pop("partial", False)
        clinic_id = self.kwargs["pk"]

        # Validate request data
        # Type hint giúp IDE autocomplete validated_data
        serializer: ClinicUpdateSerializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            # GỌI SERVICE LAYER để update clinic
            clinic = ClinicService.update_clinic(clinic_id, serializer.validated_data)

            # Trả về data đầy đủ
            response_serializer = ClinicSerializer(clinic)
            return Response(response_serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /clinics/{id}/
        Cập nhật một phần thông tin phòng khám
        """
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request: dict[str, Any], *args, **kwargs):
        """
        DELETE /clinics/{id}/
        """
        clinic_id = self.kwargs["pk"]
        try:
            # Lấy tên clinic trước khi xóa
            clinic = ClinicService.get_clinic_by_id(clinic_id)
            clinic_name = clinic.name

            # GỌI SERVICE LAYER để xóa clinic
            ClinicService.delete_clinic(clinic_id)

            return Response(
                {"message": f'Đã xóa phòng khám "{clinic_name}" thành công'},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """
        Custom action: Lấy danh sách các phòng khám đang hoạt động
        Endpoint: GET /clinics/active/
        @action decorator giải thích:
        - detail=False: Không cần {id} trong URL (/clinics/active/ thay vì /clinics/{id}/active/)
        - methods=['get']: Chỉ cho phép HTTP GET method
        Tham khảo: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
        Returns:
            Response: JSON với count và results
        """
        # GỌI SERVICE LAYER để lấy active clinics
        queryset = ClinicService.get_active_clinics()
        serializer = ClinicListSerializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """
        Custom action: Kích hoạt phòng khám
        Endpoint: POST /clinics/{id}/activate/
        @action decorator giải thích:
        - detail=True: CẦN {id} trong URL (/clinics/{id}/activate/)
        - methods=['post']: Chỉ cho phép HTTP POST (vì thay đổi state)
        Args:
            request: HTTP Request object
            pk (int): Primary key của clinic (lấy từ URL)
        Returns:
            Response: JSON với message và data đã update
        """
        try:
            # GỌI SERVICE LAYER để activate clinic
            clinic = ClinicService.activate_clinic(pk)

            # Serialize data để trả về
            serializer = ClinicSerializer(clinic)
            return Response(
                {
                    "message": f'Đã kích hoạt phòng khám "{clinic.name}" thành công',
                    "data": serializer.data,
                }
            )
        except ValidationError as e:
            # Xử lý lỗi từ Service layer
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """
        Custom action: Vô hiệu hóa phòng khám
        Endpoint: POST /clinics/{id}/deactivate/
        @action decorator giải thích:
        - detail=True: CẦN {id} trong URL (/clinics/{id}/deactivate/)
        - methods=['post']: Chỉ cho phép HTTP POST (vì thay đổi state)
        Args:
            request: HTTP Request object
            pk (int): Primary key của clinic (lấy từ URL)
        Returns:
            Response: JSON với message và data đã update
        """
        try:
            # GỌI SERVICE LAYER để deactivate clinic
            clinic = ClinicService.deactivate_clinic(pk)
            # Serialize data để trả về
            serializer = ClinicSerializer(clinic)
            return Response(
                {
                    "message": f'Đã vô hiệu hóa phòng khám "{clinic.name}" thành công',
                    "data": serializer.data,
                }
            )
        except ValidationError as e:
            # Xử lý lỗi từ Service layer
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
