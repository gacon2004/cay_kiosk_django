"""
CONTROLLER LAYER - Patient Views
Xử lý các request liên quan đến bệnh nhân
"""

from apps.kiosk.models import Patients
from apps.kiosk.serializers import (
    PatientDetailSerializer,
    PatientListSerializer,
    PatientSerializer,
)
from apps.kiosk.serializers.insurance_serializer import InsuranceSerializer
from apps.kiosk.services import PatientService
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class PatientViewSet(viewsets.ModelViewSet):
    """
    CONTROLLER - Patient Management ViewSet

    Xử lý CRUD operations cho bệnh nhân:
    - GET /api/patients/ - Lấy danh sách bệnh nhân
    - POST /api/patients/ - Tạo bệnh nhân mới
    - GET /api/patients/{id}/ - Xem chi tiết bệnh nhân
    - PUT /api/patients/{id}/ - Cập nhật bệnh nhân
    - PATCH /api/patients/{id}/ - Cập nhật một phần
    - DELETE /api/patients/{id}/ - Xóa bệnh nhân

    Custom actions:
    - GET /api/patients/with_insurance/ - Lấy danh sách bệnh nhân có BHYT
    - GET /api/patients/search_by_citizen_id/?citizen_id=xxx - Tìm theo CMND
    """

    queryset = Patients.objects.all()
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings

    # Filters, Search, Ordering
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["citizen_id", "fullname", "phone"]
    filterset_fields = ["gender", "ethnicity"]
    ordering_fields = ["created_at", "fullname", "date_of_birth"]
    ordering = ["-fullname"]

    def get_serializer_class(self):
        """Chọn serializer phù hợp với action"""
        if self.action == "list":
            return PatientListSerializer
        elif self.action == "retrieve":
            return PatientDetailSerializer
        return PatientSerializer

    def create(self, request, *args, **kwargs):
        """POST /api/patients/ - Tạo bệnh nhân mới qua service"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Gọi service để tạo patient (không kèm bảo hiểm)
            patient, _ = PatientService.create_patient_with_insurance(
                patient_data=serializer.validated_data
            )

            # Trả về response
            response_serializer = PatientDetailSerializer(patient)
            return Response(
                {
                    "message": "Tạo hồ sơ bệnh nhân thành công!",
                    "patient": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def with_insurance(self, request):
        """
        GET /api/patients/with_insurance/
        Lấy danh sách bệnh nhân có bảo hiểm hợp lệ
        """
        try:
            patients = PatientService.get_patients_with_valid_insurance()
            serializer = self.get_serializer(patients, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def search_by_citizen_id(self, request):
        """
        GET /api/patients/search_by_citizen_id/?citizen_id=xxx
        Tìm bệnh nhân theo CMND/CCCD qua service
        """
        citizen_id = request.query_params.get("citizen_id", None)

        if not citizen_id:
            return Response(
                {"error": "Vui lòng cung cấp số CMND/CCCD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            patient = PatientService.find_patient_by_citizen_id(citizen_id)
            if not patient:
                return Response(
                    {"error": "Không tìm thấy bệnh nhân với CMND/CCCD này"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = PatientDetailSerializer(patient)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT /api/patients/{id}/ - Cập nhật bệnh nhân qua service"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            patient = PatientService.update_patient_info(
                citizen_id=instance.citizen_id, update_data=serializer.validated_data
            )
            response_serializer = PatientDetailSerializer(patient)
            return Response(
                {
                    "message": "Cập nhật hồ sơ bệnh nhân thành công!",
                    "patient": response_serializer.data,
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
