"""
CONTROLLER LAYER - Insurance Views
Xử lý các request liên quan đến bảo hiểm y tế
"""

from datetime import date, timedelta

from apps.kiosk.models import Insurance
from apps.kiosk.serializers import InsuranceListSerializer, InsuranceSerializer
from apps.kiosk.services.patient_service import PatientService
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from kiosk.services.insurance_service import InsuranceService
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


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

    queryset = InsuranceService.get_all_insurances()
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings

    # Filters, Search, Ordering
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["insurance_id", "citizen_id", "fullname"]
    filterset_fields = ["insurance_id", "citizen_id"]
    ordering_fields = ["valid_from", "expired"]
    ordering = ["-valid_from"]

    def get_serializer_class(self):
        """Chọn serializer phù hợp với action"""
        if self.action == "list":
            return InsuranceListSerializer
        return InsuranceSerializer

    @action(detail=False, methods=["get"])
    def valid(self, request):
        """
        GET /api/insurance/valid/
        Lấy danh sách thẻ BHYT còn hiệu lực
        """
        valid_insurances = InsuranceService.get_all_valid_insurances()
        serializer = self.get_serializer(valid_insurances, many=True)
        return Response({"count": valid_insurances.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def expired(self, request):
        """
        GET /api/insurance/expired/
        Lấy danh sách thẻ BHYT đã hết hạn
        """
        expired_insurances = InsuranceService.get_all_expired_insurances()
        serializer = self.get_serializer(expired_insurances, many=True)
        return Response(
            {"count": expired_insurances.count(), "results": serializer.data}
        )

    @action(detail=False, methods=["get"])
    def expiring_soon(self, request):
        """
        GET /api/insurance/expiring_soon/?days=30
        Lấy danh sách thẻ BHYT sắp hết hạn (mặc định 30 ngày)
        """
        days = int(request.query_params.get("days", 30))
        expiring_insurances = InsuranceService.get_expiring_soon(days)

        serializer = self.get_serializer(expiring_insurances, many=True)
        return Response(
            {
                "count": expiring_insurances.count(),
                "message": f"Danh sách thẻ BHYT sắp hết hạn trong {days} ngày tới",
                "results": serializer.data,
            }
        )

    @action(detail=True, methods=["get"])
    def check_validity(self, request, pk=None):
        """
        GET /api/insurance/{id}/check_validity/
        Kiểm tra tính hợp lệ của thẻ BHYT
        """
        insurance: Insurance = self.get_object()
        # Đồng bộ trạng thái bảo hiểm cho bệnh nhân
        PatientService.sync_patient_insurance_status(insurance.citizen_id)

        validity_info = InsuranceService.check_insurance_validity(insurance)
        return Response(validity_info)

    def create(self, request, *args, **kwargs):
        """POST /api/insurance/ - Tạo bảo hiểm mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Gọi service để tạo insurance với validation đầy đủ
            insurance = InsuranceService.create_insurance(serializer.validated_data)

            # Đồng bộ trạng thái bảo hiểm cho patient
            PatientService.sync_patient_insurance_status(
                serializer.validated_data["citizen_id"]
            )

            # Serialize lại insurance vừa tạo để trả response
            response_serializer = self.get_serializer(insurance)
            return Response(
                {
                    "message": "Thêm thẻ bảo hiểm thành công!",
                    "insurance": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
