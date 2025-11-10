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
    - POST /api/patients/register_from_insurance/ - Tạo patient từ BHYT (nếu chưa có)
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
    ordering_fields = ["created_at", "fullname", "dob"]
    ordering = ["-fullname"]

    def get_serializer_class(self):
        """Chọn serializer phù hợp với action"""
        if self.action == "list":
            return PatientListSerializer
        elif self.action == "retrieve":
            return PatientDetailSerializer
        return PatientSerializer

    def create(self, request, *args, **kwargs):
        """POST /api/patients - Tạo bệnh nhân mới qua service"""
        # Log data nhận được từ frontend để debug
        print("=== RECEIVED DATA FROM FRONTEND ===")
        print(f"Raw data: {request.data}")
        print("===================================")

        # Map field names từ frontend sang backend format
        mapped_data = request.data.copy()

        # Không cần map phone nữa vì frontend đã gửi phone_number
        # Convert gender từ string sang boolean
        if "gender" in mapped_data:
            if mapped_data["gender"] == "male":
                mapped_data["gender"] = True
            elif mapped_data["gender"] == "female":
                mapped_data["gender"] = False

        print("=== MAPPED DATA FOR SERIALIZER ===")
        print(f"Mapped data: {mapped_data}")
        print("===================================")

        serializer = self.get_serializer(data=mapped_data)
        serializer.is_valid(raise_exception=True)

        print("=== VALIDATED DATA ===")
        print(f"Validated data: {serializer.validated_data}")
        print("======================")

        try:
            # Gọi service để tạo patient (không kèm bảo hiểm)
            patient, _ = PatientService.create_patient(
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
            print(f"=== ERROR CREATING PATIENT ===")
            print(f"Error: {str(e)}")
            print("================================")
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

    @action(detail=False, methods=["post"])
    def check_insurance(self, request):
        """
        POST /api/patients/check_insurance
        Kiểm tra thông tin bảo hiểm y tế và tạo hồ sơ bệnh nhân nếu chưa tồn tại

        Body: { "citizen_id": "string" }

        Flow:
        1. Kiểm tra thẻ BHYT có tồn tại không
        2. Nếu có BHYT, hiển thị thông tin bảo hiểm
        3. Nếu chưa có patient thì tạo mới với các trường từ BHYT: citizen_id, fullname, gender, dob, phone_number
        4. Trả về chi tiết thông tin bảo hiểm y tế
        """
        citizen_id = request.data.get("citizen_id")

        if not citizen_id:
            return Response(
                {"error": "Vui lòng cung cấp số CMND/CCCD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Kiểm tra thẻ bảo hiểm có tồn tại không
            from apps.kiosk.services.insurance_service import InsuranceService

            insurance = InsuranceService.get_insurance_by_citizen_id(citizen_id)

            if not insurance:
                return Response(
                    {
                        "error": "Không tìm thấy thẻ bảo hiểm y tế với CMND/CCCD này",
                        "message": "Vui lòng đăng ký hồ sơ bệnh nhân trước",
                        "action_required": "register_patient",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Kiểm tra bệnh nhân đã tồn tại chưa
            existing_patient = PatientService.find_patient_by_citizen_id(citizen_id)

            if existing_patient:
                # Nếu đã có patient, trả về thông tin
                serializer = PatientDetailSerializer(existing_patient)
                return Response(
                    {
                        "message": "Bệnh nhân đã tồn tại trong hệ thống",
                        "patient": serializer.data,
                        "insurance": InsuranceSerializer(insurance).data,
                        "has_patient": True,
                    }
                )

            # Nếu chưa có patient, tạo mới với thông tin từ bảo hiểm
            patient = PatientService.create_patient_with_non_insur(
                citizen_id=citizen_id,
                fullname=insurance.fullname,
                phone_number=insurance.phone_number,  # Lấy từ bảo hiểm
                occupation="",  # Để trống, sẽ cập nhật sau
                dob=insurance.dob,
                ethnicity="",  # Để trống, sẽ cập nhật sau
                address="",  # Để trống, sẽ cập nhật sau
                gender=getattr(insurance, "gender", ""),
            )

            # Đồng bộ trạng thái bảo hiểm
            PatientService.sync_patient_insurance_status(citizen_id)

            # Trả về response
            patient_serializer = PatientDetailSerializer(patient)
            insurance_serializer = InsuranceSerializer(insurance)

            return Response(
                {
                    "message": "Tạo hồ sơ bệnh nhân từ thẻ bảo hiểm thành công!",
                    "patient": patient_serializer.data,
                    "insurance": insurance_serializer.data,
                    "has_patient": False,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
