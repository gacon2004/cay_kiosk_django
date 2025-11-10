from apps.kiosk.models import ServiceExam
from apps.kiosk.serializers import ServiceExamsListSerializer
from apps.kiosk.services.exam_service import ExamService
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class ServiceExamViewSet(viewsets.ModelViewSet):
    """
    CONTROLLER - Service Exam Management ViewSet

    Xử lý CRUD operations cho dịch vụ khám:
    - GET /api/service-exams - Lấy danh sách dịch vụ khám
    - POST /api/service-exams/ - Tạo dịch vụ khám mới
    - GET /api/service-exams/{id}/ - Xem chi tiết dịch vụ khám
    - PUT /api/service-exams/{id}/ - Cập nhật dịch vụ khám
    - PATCH /api/service-exams/{id}/ - Cập nhật một phần
    - DELETE /api/service-exams/{id}/ - Xóa dịch vụ khám
    """

    # Gọi service thay vì model trực tiếp
    queryset = ExamService.get_all_exams()
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings

    # Filters, Search, Ordering
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = ["name"]
    ordering_fields = ["name", "prices_non_insurance", "prices_insurance"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
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

    def create(self, request, *args, **kwargs):
        """POST /api/kiosk/service_exams/ - Tạo dịch vụ khám mới"""
        # Validate input data
        name = request.data.get("name")
        description = request.data.get("description", "")
        price_non_insurance_str = request.data.get("prices_non_insurance")
        price_insurance_str = request.data.get("prices_insurance")

        if not all(
            [name, price_non_insurance_str is not None, price_insurance_str is not None]
        ):
            return Response(
                {
                    "error": "Thiếu thông tin bắt buộc: name, prices_non_insurance, prices_insurance"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            price_non_insurance = float(price_non_insurance_str)  # type: ignore
            price_insurance = float(price_insurance_str)  # type: ignore
        except (ValueError, TypeError):
            return Response(
                {"error": "Giá dịch vụ phải là số hợp lệ"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Gọi service để tạo
            exam = ExamService.create_service_exam(
                name=str(name),
                description=str(description),
                price_non_insurance=price_non_insurance,
                price_insurance=price_insurance,
            )

            # Serialize response
            serializer = self.get_serializer(exam)
            return Response(
                {"message": "Tạo dịch vụ khám thành công!", "exam": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Lỗi hệ thống: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """PUT /api/kiosk/service_exams/{id}/ - Cập nhật dịch vụ khám"""
        instance = self.get_object()

        try:
            # Gọi service để update
            updated_exam = ExamService.update_service_exam(instance, request.data)

            # Serialize response
            serializer = self.get_serializer(updated_exam)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Lỗi cập nhật: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/kiosk/service_exams/{id}/ - Xóa dịch vụ khám"""
        instance = self.get_object()

        try:
            ExamService.delete_service_exam(instance)
            return Response(
                {"message": "Xóa dịch vụ khám thành công!"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": f"Lỗi xóa: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        GET /api/kiosk/service_exams/search/?q=search_term
        Tìm kiếm dịch vụ khám theo từ khóa
        """
        search_term = request.query_params.get("q", "")
        if not search_term:
            return Response(
                {"error": "Thiếu tham số tìm kiếm 'q'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exams = ExamService.search_exams(search_term)
        serializer = self.get_serializer(exams, many=True)
        return Response({"count": exams.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def by_price_range(self, request):
        """
        GET /api/kiosk/service_exams/by_price_range/?min=100000&max=500000
        Lấy dịch vụ khám trong khoảng giá
        """
        try:
            min_price = float(request.query_params.get("min", 0))
            max_price = float(request.query_params.get("max", 999999999))

            exams = ExamService.get_exams_by_price_range(min_price, max_price)
            serializer = self.get_serializer(exams, many=True)
            return Response(
                {
                    "count": exams.count(),
                    "price_range": f"{min_price} - {max_price}",
                    "results": serializer.data,
                }
            )
        except ValueError:
            return Response(
                {"error": "Giá trị min/max phải là số"},
                status=status.HTTP_400_BAD_REQUEST,
            )
