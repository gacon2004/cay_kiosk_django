"""
LEGACY FILE - Deprecated
Sử dụng views từ thư mục views/ theo cấu trúc MVC mới
File này chỉ để backward compatibility
"""

import logging
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from apps.kiosk.models import Clinic, Doctors, Insurance, Patients, Order, ServiceExam, CustomUser
from django.db import transaction
from apps.kiosk.serializer import (ClinicCreateSerializer, ClinicListSerializer, 
                                    ClinicSerializer, DoctorDetailSerializer, 
                                    DoctorListSerializer, DoctorSerializer, 
                                    InsuranceListSerializer, InsuranceSerializer, 
                                    PatientDetailSerializer, PatientListSerializer, 
                                    PatientSerializer, OrderSerializer,
                                    ServiceExamListSerializer, ServiceExamCreateSerializer,
                                    ServiceExamDetailSerializer, ServiceExamSerializer,
                                    UserListSerializer, UserCreateSerializer,UserUpdateSerializer, UserSerializer)

class ClinicViewSet(viewsets.ModelViewSet):
    """
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
    # IsAuthenticated = Chỉ user đã đăng nhập mới được truy cập
    # PRODUCTION READY: Phân quyền theo role và action
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Override method get_permissions() để customize permission cho từng action

        LOGIC PHÂN QUYỀN:
        - Read operations (list, retrieve, active): IsAuthenticated (user đã login)
        - Write operations (create, update, partial_update, destroy): IsAdminUser (chỉ admin)
        - Special actions (activate, deactivate): IsAdminUser (chỉ admin)

        Returns:
            list: Danh sách permission instances
        """
        # Admin only actions (CUD + activate/deactivate)
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "activate",
            "deactivate",
        ]:
            return [IsAuthenticated(), IsAdminUser()]

        # Authenticated user actions (Read operations)
        return [IsAuthenticated()]

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

        queryset = Clinic.objects.all().order_by("name")
        # Filter theo trạng thái
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        # Search theo tên
        if search:
            queryset = queryset.filter(name__icontains=search)
        # Serialize data
        # Type hint giúp IDE biết serializer type
        serializer = self.get_serializer(queryset, many=True)

        return Response({"count": queryset.count(), "results": serializer.data})

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        POST /clinics
        """
        # Validate request data với serializer
        serializer = self.get_serializer(data=request.data)
        logging.info(f"Clinic create request data: {request.data}")
        serializer.is_valid(raise_exception=True)

        try:
            clinic = serializer.save()  # Tạo clinic trực tiếp từ serializer
            # Trả về data đầy đủ
            create_response_serializer = ClinicCreateSerializer(clinic)
            return Response(
                create_response_serializer.data, status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response({"error": {str(e)}}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        GET /clinics/{id}
        """
        try:
            # GỌI SERVICE LAYER để lấy clinic
            clinic = Clinic.objects.get(id=self.kwargs["pk"])
            # Type hint giúp IDE autocomplete
            serializer = self.get_serializer(clinic)
            return Response(serializer.data)
        except Clinic.DoesNotExist:
            return Response(
                {"error": f"Không tìm thấy phòng khám với ID {self.kwargs['pk']}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response(
                {
                    "error": f"Không tìm thấy phòng khám với ID {self.kwargs['pk']} / {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        PUT /clinics/{id}/
        Cập nhật toàn bộ thông tin phòng khám
        """
        partial = kwargs.pop(
            "partial", False
        )  # yêu cầu tất cả fields phải có trong request nếu partial=False, còn true thì chỉ cần một phần được cung cấp
        clinic_id = self.kwargs["pk"]  # lấy id từ url
        # Validate request data
        serializer = self.get_serializer(
            data=request.data, partial=partial
        )  # tạo serializer với data từ request
        serializer.is_valid(raise_exception=True)

        try:
            if Clinic.objects.filter(id=clinic_id).exists() is False:
                raise ValidationError(f"Không tìm thấy phòng khám với ID {clinic_id}")

            clinic = Clinic.objects.get(id=clinic_id)
            # Validate tên không trùng (nếu update tên)
            new_name = serializer.validated_data.get("name")
            if new_name:
                new_name = new_name.strip()
                if (
                    Clinic.objects.exclude(pk=clinic.pk)
                    .filter(name__iexact=new_name)
                    .exists()
                ):
                    raise ValidationError(f"Phòng khám '{new_name}' đã tồn tại")
            # Cập nhật các fields đã validated
            for key, value in serializer.validated_data.items():
                if hasattr(clinic, key):
                    setattr(clinic, key, value)
            clinic.full_clean()  # kiểm tra dữ liệu, đảm bảo dữ liệu hợp lệ trước khi lưu
            clinic.save()

            # Trả về data đầy đủ
            response_serializer = ClinicSerializer(clinic)
            return Response(response_serializer.data)
        except Clinic.DoesNotExist:
            return Response(
                {"error": f"Không tìm thấy phòng khám với ID {clinic_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /clinics/{id}/
        Cập nhật một phần thông tin phòng khám
        """
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /clinics/{id}/
        """
        clinic_id = self.kwargs["pk"]
        try:
            # Lấy tên clinic trước khi xóa
            clinic = Clinic.objects.get(id=clinic_id)
            clinic_name = clinic.name
            clinic.delete()

            return Response(
                {"message": f'Đã xóa phòng khám "{clinic_name}" thành công'},
                status=status.HTTP_200_OK,
            )
        except Clinic.DoesNotExist:
            return Response(
                {"error": f"Không tìm thấy phòng khám với ID {clinic_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """
        Custom action: Lấy danh sách các phòng khám đang hoạt động
        Endpoint: GET /clinics/active
        @action decorator giải thích:
        - detail=False: Không cần {id} trong URL (/clinics/active thay vì /clinics/{id}/active)
        - methods=['get']: Chỉ cho phép HTTP GET method
        Tham khảo: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
        """

        try:
            queryset = Clinic.objects.filter(is_active=True).order_by("name")
            serializer = ClinicListSerializer(queryset, many=True)
            return Response({"count": queryset.count(), "results": serializer.data})
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """
        Custom action: Kích hoạt phòng khám
        Endpoint: POST /clinics/{id}/activate
        @action decorator giải thích:
        - detail=True: CẦN {id} trong URL (/clinics/{id}/activate)
        - methods=['post']: Chỉ cho phép HTTP POST (vì thay đổi state)
        Args:
            request: HTTP Request object
            pk (int): Primary key của clinic (lấy từ URL)
        Returns:
            Response: JSON với message và data đã update
        """
        if pk is None:
            return Response(
                {"error": "Clinic ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # GỌI SERVICE LAYER để activate clinic
            clinic_id = self.kwargs.get("pk", None)
            clinic = Clinic.objects.get(id=clinic_id) # +1 query to get clinic

            clinic.is_active = True
            clinic.save() # + 1 query to save clinic

            # Serialize data để trả về
            serializer = ClinicSerializer(clinic)
            return Response(
                {
                    "message": f'Đã kích hoạt phòng khám "{clinic.name}" thành công',
                    "data": serializer.data,
                }
            )
        except Clinic.DoesNotExist:
            return Response(
                {"error": f"Không tìm thấy phòng khám với ID {clinic_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            # Xử lý lỗi từ Service layer
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    @transaction.atomic
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
        if pk is None:
            return Response(
                {"error": "Clinic ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            clinic = Clinic.objects.get(id=pk)
            clinic.is_active = False
            clinic.save()
            # Serialize data để trả về
            serializer = ClinicSerializer(clinic)
            return Response(
                {
                    "message": f'Đã vô hiệu hóa phòng khám "{clinic.name}" thành công',
                    "data": serializer.data,
                }
            )
        except Clinic.DoesNotExist:
            return Response(
                {"error": f"Không tìm thấy phòng khám với ID {pk}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            # Xử lý lỗi từ Service layer
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

# ------------------- Doctor ViewSet ------------------ #

class DoctorViewSet(viewsets.ModelViewSet):
    """
    Xử lý CRUD operations cho bác sĩ:
    - GET /api/doctors/ - Lấy danh sách bác sĩ
    - POST /api/doctors/ - Tạo bác sĩ mới
    - GET /api/doctors/{id}/ - Xem chi tiết bác sĩ
    - PUT /api/doctors/{id}/ - Cập nhật bác sĩ
    - PATCH /api/doctors/{id}/ - Cập nhật một phần
    - DELETE /api/doctors/{id}/ - Xóa bác sĩ
    
    Custom actions:
    - GET /api/doctors/by_specialization/?spec=xxx - Tìm theo chuyên khoa
    - GET /api/doctors/active/ - Lấy danh sách bác sĩ đang hoạt động
    - POST /api/doctors/{id}/activate/ - Kích hoạt bác sĩ
    - POST /api/doctors/{id}/deactivate/ - Vô hiệu hóa bác sĩ
    """
    
    queryset = Doctors.objects.all() # đọc dữ liệu từ model Doctors
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings
    
    # Filters, Search, Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['doctor_id', 'full_name', 'specialization', 'email']
    filterset_fields = ['specialization', 'is_active']
    ordering_fields = ['created_at', 'full_name', 'years_of_experience']
    ordering = ['full_name']
    
    def get_serializer_class(self):
        """Chọn serializer phù hợp với action"""
        if self.action == 'list':
            return DoctorListSerializer
        elif self.action == 'retrieve':
            return DoctorDetailSerializer
        return DoctorSerializer
    
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
    #     """Phân quyền - Chỉ admin mới có quyền tạo, sửa, xóa bác sĩ"""
    #     if self.action in ['create', 'update', 'partial_update', 'destroy', 'activate', 'deactivate']:
    #         return [permissions.IsAdminUser()]
    #     return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def by_specialization(self, request):
        """
        GET /api/users/doctors/by_specialization/?spec=Tim mạch
        Tìm bác sĩ theo chuyên khoa
        """
        specialization = request.query_params.get('spec', None)
        
        if not specialization:
            return Response({
                'error': 'Vui lòng cung cấp tên chuyên khoa (spec)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        doctors = Doctors.objects.filter(
            specialization__icontains=specialization,
            is_active=True
        )
        
        serializer = self.get_serializer(doctors, many=True)
        return Response({
            'specialization': specialization,
            'count': doctors.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        GET /api/users/doctors/active/
        Lấy danh sách bác sĩ đang hoạt động
        """
        active_doctors = Doctors.objects.filter(is_active=True)
        serializer = self.get_serializer(active_doctors, many=True)
        return Response({
            'count': active_doctors.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """
        POST /api/users/doctors/{id}/activate/
        Kích hoạt bác sĩ
        """
        doctor = self.get_object()
        doctor.is_active = True
        doctor.save()
        
        return Response({
            'message': f'Đã kích hoạt bác sĩ {doctor.full_name}',
            'doctor': DoctorSerializer(doctor).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """
        POST /api/users/doctors/{id}/deactivate/
        Vô hiệu hóa bác sĩ
        """
        doctor = self.get_object()
        doctor.is_active = False
        doctor.save()
        
        return Response({
            'message': f'Đã vô hiệu hóa bác sĩ {doctor.full_name}',
            'doctor': DoctorSerializer(doctor).data
        })
    
    @action(detail=False, methods=['get'])
    def specializations(self, request):
        """
        GET /api/users/doctors/specializations/
        Lấy danh sách các chuyên khoa có sẵn
        """
        specializations = Doctors.objects.values_list('specialization', flat=True).distinct()
        
        return Response({
            'count': len(specializations),
            'specializations': list(specializations)
        })
    
    def create(self, request, *args, **kwargs):
        """POST /api/users/doctors/ - Tạo bác sĩ mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'message': 'Thêm bác sĩ mới thành công!',
            'doctor': serializer.data
        }, status=status.HTTP_201_CREATED)
        

class InsuranceViewSet(viewsets.ModelViewSet):
    """
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
    """

    queryset = Insurance.objects.all()
    # permission_classes = [permissions.IsAuthenticated]  # Comment để dùng AllowAny từ settings

    # Filters, Search, Ordering
    filter_backends = [
        DjangoFilterBackend, # Dùng để filter theo field cụ thể (ví dụ ?specialization=Tim+mạch), Hỗ trợ các lookup (exact, lt, gt,...) nếu bạn định nghĩa filterset hoặc dùng tên field__lookup trong query params
        filters.SearchFilter, #tìm kiếm text với param mặc định ?search=..., Hỗ trợ tiền tố đặc biệt ( '^', '=' , '@' ) nếu muốn thay đổi kiểu tìm, Tìm trên các trường đã khai báo trong search_fields (ví dụ ['fullname', 'email']) bằng phép contains (mặc định là icontains).
        filters.OrderingFilter, #Dùng để sắp xếp kết quả với param ?ordering=field (ví dụ ?ordering=-created_at để giảm dần), Cho phép chỉ định ordering_fields để giới hạn các trường được sắp xếp
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
        GET /api/insurance/valid
        Lấy danh sách thẻ BHYT còn hiệu lực
        """
        valid_insurances = Insurance.objects.filter(is_valid=True)
        serializer = self.get_serializer(valid_insurances, many=True)
        return Response({"count": valid_insurances.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def expired(self, request):
        """
        GET /api/insurance/expired
        Lấy danh sách thẻ BHYT đã hết hạn
        """
        expired_insurances = Insurance.objects.filter(is_valid=False)
        serializer = self.get_serializer(expired_insurances, many=True)
        return Response(
            {"count": expired_insurances.count(), "results": serializer.data}
        )

    def create(self, request, *args, **kwargs):
        """POST /api/insurance/ - Tạo bảo hiểm mới"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Gọi service để tạo insurance với validation đầy đủ
            insurance = Insurance.objects.create(**serializer.validated_data)
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


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Endpoint tùy chỉnh để cập nhật trạng thái"""
        order: Order = self.get_object()
        new_status = request.data.get('order_status')
        if new_status not in dict(Order.ORDER_STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        order.order_status = new_status
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

class PatientViewSet(viewsets.ModelViewSet):
    """
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
        print(f"Raw data: {request.data}")
        # Map field names từ frontend sang backend format
        mapped_data = request.data.copy()
        # Không cần map phone nữa vì frontend đã gửi phone_number
        # Convert gender từ string sang boolean
        if "gender" in mapped_data:
            if mapped_data["gender"] == "male":
                mapped_data["gender"] = True
            elif mapped_data["gender"] == "female":
                mapped_data["gender"] = False
        print(f"Mapped data: {mapped_data}")
        serializer = self.get_serializer(data=mapped_data)
        serializer.is_valid(raise_exception=True)
        print(f"Validated data: {serializer.validated_data}")

        try:
            # Gọi service để tạo patient (không kèm bảo hiểm)
            patient = Patients.objects.create(**serializer.validated_data)
            print(f"Created patient: {patient}")

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
            print(f"Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def with_insurance(self, request):
        """
        GET /api/patients/with_insurance/
        Lấy danh sách bệnh nhân có bảo hiểm hợp lệ
        """
        try:
            patients = Patients.objects.filter(is_insurance=True)
            serializer = self.get_serializer(patients, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def search_by_citizen_id(self, request):
        """
        GET /api/patients/search_by_citizen_id/?citizen_id=xxx
        Tìm bệnh nhân theo CCCD qua service
        """
        citizen_id = request.query_params.get("citizen_id", None)

        if not citizen_id:
            return Response(
                {"error": "Vui lòng cung cấp số CCCD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            patient = Patients.objects.get(citizen_id=citizen_id)
            serializer = PatientDetailSerializer(patient)
            return Response(serializer.data)
        except Patients.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy bệnh nhân với CCCD này"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT /api/patients/{id} - Cập nhật bệnh nhân qua service"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                patient = serializer.save()   # gọi ModelSerializer.update() rồi instance.save()
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
                {"error": "Vui lòng cung cấp số CCCD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Kiểm tra thẻ bảo hiểm có tồn tại không
            insurance = Insurance.objects.get(citizen_id=citizen_id)

            if not insurance:
                return Response(
                    {
                        "error": "Không tìm thấy thẻ bảo hiểm y tế với CCCD này",
                        "message": "Vui lòng đăng ký hồ sơ bệnh nhân trước",
                        "action_required": "register_patient",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Kiểm tra bệnh nhân đã tồn tại chưa
            existing_patient =Patients.objects.get(citizen_id=citizen_id)
            if existing_patient:
                # Nếu đã có patient, trả về thông tin bảo hiểm
                return Response(
                    {
                        "message": "Bệnh nhân đã tồn tại trong hệ thống",
                        "insurance": InsuranceSerializer(insurance).data,
                        "has_patient": True,
                    }
                )
            elif not existing_patient:
                # Nếu chưa có patient, tạo mới với thông tin từ bảo hiểm
                patient = Patients.objects.create(
                    citizen_id=citizen_id,
                    fullname=insurance.fullname,
                    phone_number=insurance.phone_number,  # Lấy từ bảo hiểm
                    occupation="",  # Để trống, sẽ cập nhật sau
                    dob=insurance.dob,
                    ethnicity="",  # Để trống, sẽ cập nhật sau
                    address="",  # Để trống, sẽ cập nhật sau
                    gender=getattr(insurance, "gender", ""),
                    is_insurance=True,
                )
                patient.save()
            # Trả về response
            insurance_serializer = InsuranceSerializer(insurance)
            return Response(
                {
                    "message": "Tạo hồ sơ bệnh nhân từ thẻ bảo hiểm thành công!",
                    "insurance": insurance_serializer.data,
                    "has_patient": False,
                },
                status=status.HTTP_201_CREATED,
            )
        except Insurance.DoesNotExist:
            return Response(
                {
                    "error": "Không tìm thấy thẻ bảo hiểm y tế với CCCD này",
                    "message": "Vui lòng đăng ký hồ sơ bệnh nhân trước",
                    "action_required": "register_patient",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ServiceExamViewSet(viewsets.ModelViewSet):
    """
    Xử lý CRUD operations cho dịch vụ khám:
    - GET /api/service-exams - Lấy danh sách dịch vụ khám
    - POST /api/service-exams/ - Tạo dịch vụ khám mới
    - GET /api/service-exams/{id}/ - Xem chi tiết dịch vụ khám
    - PUT /api/service-exams/{id}/ - Cập nhật dịch vụ khám
    - PATCH /api/service-exams/{id}/ - Cập nhật một phần
    - DELETE /api/service-exams/{id}/ - Xóa dịch vụ khám
    """

    # Gọi service thay vì model trực tiếp
    queryset = ServiceExam.objects.all()
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
            return ServiceExamListSerializer
        elif self.action == "retrieve":
            return ServiceExamDetailSerializer
        elif self.action == "create":
            return ServiceExamCreateSerializer
        return ServiceExamSerializer

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

        if not all([name, price_non_insurance_str is not None, price_insurance_str is not None]):
            return Response(
                {"error": "Thiếu thông tin bắt buộc: name, prices_non_insurance, prices_insurance"},
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
            exam = ServiceExam.objects.create(name=str(name),
                                              description=str(description),
                                              prices_non_insurance=price_non_insurance,
                                              prices_insurance=price_insurance)
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
        partial = kwargs.pop("partial", False)
        instance = self.get_object()  # Lấy instance theo ID từ URL

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                updated_exam = serializer.save()  # Cập nhật instance
            # Serialize response
            return Response(self.get_serializer(updated_exam).data)
        except Exception as e:
            return Response(
                {"error": f"Lỗi cập nhật: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request: Request, *args, **kwargs) -> Response: #tên method mặc định trong ModelViewSet
        """DELETE /api/kiosk/service_exams/{id}/ - Xóa dịch vụ khám"""
        instance: ServiceExam = self.get_object()

        try:
            instance.delete()  # Xóa instance
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

        exams = ServiceExam.objects.filter(name__icontains=search_term)
        serializer = self.get_serializer(exams, many=True)
        return Response({"count": exams.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def by_price_range_insurance(self, request):
        """
        GET /api/kiosk/service_exams/by_price_range_insurance/?min=100000&max=500000&price_type=insurance
        Lấy dịch vụ khám trong khoảng giá bảo hiểm hoặc không bảo hiểm
        price_type: 'insurance' (mặc định) hoặc 'non_insurance'
        """
        try:
            min_price = float(request.query_params.get("min", 0))
            max_price = float(request.query_params.get("max", 100000000))
            price_type = request.query_params.get("price_type", "insurance")  # Mặc định là insurance

            if price_type == "insurance":
                exams = ServiceExam.objects.filter(prices_insurance__gte=min_price,
                                                  prices_insurance__lte=max_price)
            elif price_type == "non_insurance":
                exams = ServiceExam.objects.filter(prices_non_insurance__gte=min_price,
                                                  prices_non_insurance__lte=max_price)
            else:
                return Response(
                    {"error": "price_type phải là 'insurance' hoặc 'non_insurance'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(exams, many=True)
            return Response(
                {
                    "count": exams.count(),
                    "price_range": f"{min_price} - {max_price}",
                    "price_type": price_type,
                    "results": serializer.data,
                }
            )
        except ValueError:
            return Response(
                {"error": "Giá trị min/max phải là số"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
class UserViewSet(viewsets.ModelViewSet):
    """
    Xử lý CRUD operations cho User:
    - GET /api/users - Lấy danh sách users
    - POST /api/users - Tạo user mới (chỉ admin)
    - GET /api/users/{id} - Xem chi tiết user
    - PUT /api/users/{id} - Cập nhật user (toàn bộ)
    - PATCH /api/users/{id} - Cập nhật user (một phần)
    - DELETE /api/users/{id} - Xóa user (chỉ admin)
    
    Custom actions:
    - GET /api/users/me - Lấy thông tin user hiện tại
    - GET /api/users/active - Lấy danh sách users active
    - POST /api/users/{id}/activate - Kích hoạt user
    - POST /api/users/{id}/deactivate - Vô hiệu hóa user
    """
    
    queryset = CustomUser.objects.all()
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
        GET /api/users/me
        Lấy thông tin user hiện tại
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        GET /api/users/active
        Lấy danh sách users đang active
        """
        active_users = CustomUser.objects.filter(is_active=True)
        serializer = self.get_serializer(active_users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """
        POST /api/users/{id}/activate
        Kích hoạt user
        """
        user: CustomUser = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({
            'message': f'User {user.username} đã được kích hoạt!',
            'user': UserSerializer(user).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """
        POST /api/users/{id}/deactivate
        Vô hiệu hóa user
        """
        user: CustomUser = self.get_object()
        user.is_active = False
        user.save()
        
        return Response({
            'message': f'User {user.username} đã bị vô hiệu hóa!',
            'user': UserSerializer(user).data
        })
    
    def destroy(self, request, *args, **kwargs):
        """DELETE /api/users/{id}/ - Xóa user (soft delete)"""
        user: CustomUser = self.get_object()
        
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
