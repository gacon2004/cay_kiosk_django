from typing import Optional, Any, Dict
from apps.kiosk.models import Clinic, Doctors, Insurance, Patients, Order, ServiceExam
from rest_framework import serializers
from datetime import date

# Constants cho validation
CLINIC_NAME_MIN_LENGTH = 3
CLINIC_NAME_MAX_LENGTH = 100
CLINIC_ADDRESS_MIN_LENGTH = 10
CLINIC_ADDRESS_MAX_LENGTH = 500

class ClinicNameValidator:
    @staticmethod
    def validate_name(name: str, exclude_pk: Optional[int] = None) -> str:
        cleaned_name = name.strip()
        if not cleaned_name:
            raise serializers.ValidationError("Tên phòng khám không được để trống")

        # Length validation
        if len(cleaned_name) < CLINIC_NAME_MIN_LENGTH:
            raise serializers.ValidationError(
                f"Tên phòng khám phải có ít nhất {CLINIC_NAME_MIN_LENGTH} ký tự"
            )

        if len(cleaned_name) > CLINIC_NAME_MAX_LENGTH:
            raise serializers.ValidationError(
                f"Tên phòng khám không được vượt quá {CLINIC_NAME_MAX_LENGTH} ký tự"
            )

        # Uniqueness check
        queryset = Clinic.objects.filter(name__iexact=cleaned_name)
        if exclude_pk:
            queryset = queryset.exclude(pk=exclude_pk)

        if queryset.exists():
            raise serializers.ValidationError("Tên phòng khám đã tồn tại")

        return cleaned_name


class ClinicValidationMixin:
    """
    Mixin class chứa các validation methods cho Clinic serializers
    Sử dụng mixin thay vì base class để linh hoạt hơn
    """

    def validate_name(self, value: str) -> str:
        return ClinicNameValidator.validate_name(value)

    def validate_address(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("Địa chỉ không được để trống")

        cleaned_address = value.strip()
        if len(cleaned_address) < CLINIC_ADDRESS_MIN_LENGTH:
            raise serializers.ValidationError(
                f"Địa chỉ phải có ít nhất {CLINIC_ADDRESS_MIN_LENGTH} ký tự"
            )

        if len(cleaned_address) > CLINIC_ADDRESS_MAX_LENGTH:
            raise serializers.ValidationError(
                f"Địa chỉ không được vượt quá {CLINIC_ADDRESS_MAX_LENGTH} ký tự"
            )

        return cleaned_address


class ClinicSerializer(ClinicValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = [
            "id",  # ID tự động tăng
            "name",  # Tên phòng khám
            "is_active",  # Trạng thái (True/False)
            "address",  # Địa chỉ
            "created_at",  # Ngày tạo
            "updated_at",  # Ngày cập nhật
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_active"]


class ClinicListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clinic
        # Chỉ lấy các fields quan trọng
        fields = ["name", "is_active", "address"]


class ClinicCreateSerializer(ClinicValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ["name", "address", "is_active"]


class ClinicUpdateSerializer(ClinicValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ["name", "address", "is_active"]

    def validate_name(self, value: str) -> str:
        # Lấy ID của clinic đang được update để exclude khỏi validation trùng tên
        exclude_pk = self.instance.pk if self.instance else None
        return ClinicNameValidator.validate_name(value, exclude_pk)

# Constants cho validation
DOCTOR_ID_PREFIX = "BS"
MAX_YEARS_EXPERIENCE = 60
MIN_YEARS_EXPERIENCE = 0

class DoctorValidators:
    @staticmethod
    def validate_doctor_id(doctor_id: str) -> str:
        # check id empty
        if not doctor_id:
            raise serializers.ValidationError("Mã bác sĩ không được để trống")
        # Clean and standardize ID
        cleaned_id = doctor_id.strip().upper()

        if not cleaned_id.startswith(DOCTOR_ID_PREFIX):
            raise serializers.ValidationError(
                f"Mã bác sĩ phải bắt đầu bằng '{DOCTOR_ID_PREFIX}'"
            )

        # Check format: BS + numbers (e.g., BS001, BS123)
        if len(cleaned_id) < 3 or not cleaned_id[2:].isdigit():
            raise serializers.ValidationError(
                "Mã bác sĩ phải có format BS + số (ví dụ: BS001)"
            )

        return cleaned_id

    @staticmethod
    def validate_years_experience(years: int) -> int:
        if not isinstance(years, int):
            raise serializers.ValidationError("Số năm kinh nghiệm phải là số nguyên")
        if years < MIN_YEARS_EXPERIENCE:
            raise serializers.ValidationError("Số năm kinh nghiệm không được âm")
        if years > MAX_YEARS_EXPERIENCE:
            raise serializers.ValidationError(
                f"Số năm kinh nghiệm không được vượt quá {MAX_YEARS_EXPERIENCE} năm"
            )
        return years

class DoctorValidationMixin:
    def validate_doctor_id(self, value: str) -> str:
        return DoctorValidators.validate_doctor_id(value)

    def validate_years_of_experience(self, value: int) -> int:
        return DoctorValidators.validate_years_experience(value)


class DoctorSerializer(DoctorValidationMixin, serializers.ModelSerializer):
    title = serializers.ReadOnlyField(help_text="Danh xưng bác sĩ")

    class Meta:
        model = Doctors
        fields = [
            "id",
            "doctor_id",
            "fullname",
            "title",
            "specialization",
            "phone",
            "email",
            "user_id",  # ID của tài khoản User liên kết (nullable)
            "years_of_experience",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "title")


class DoctorListSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField()

    class Meta:
        model = Doctors
        fields = [
            "id",
            "doctor_id",
            "fullname",
            "title",
            "specialization",
            "phone",
            "is_active",
        ]


class DoctorDetailSerializer(serializers.ModelSerializer):
    title = (
        serializers.ReadOnlyField()
    )  # chỉ hiển thị data, không cho phép khi input tạo/cập nhật
    user_info = (
        serializers.SerializerMethodField()
    )  # định nghĩa field được tính toán bởi method, hiển thị thông tin user liên kết

    class Meta:  # hứa cấu hình cho serializer (model, fields, validation, etc.), ModelSerializer đều cần Meta class
        model = Doctors  # model đại diện
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_user_info(self, obj: Doctors) -> dict | None:
        """Lấy thông tin user liên kết, tài khoản bác sĩ"""
        if obj.user_id:
            return {
                "username": obj.user_id.username,
                "email": obj.user_id.email,
                "is_active": obj.user_id.is_active,
            }
        return None

class InsuranceSerializer(serializers.ModelSerializer):

    # FIX: Định dạng ngày tháng cho HTML input type="date" (yyyy-mm-dd)
    dob = serializers.DateField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    )
    valid_from = serializers.DateField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    )
    expired = serializers.DateField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    )

    class Meta:
        model = Insurance
        fields = [
            "insurance_id",
            "citizen_id",
            "fullname",
            "gender",
            "dob",
            "phone_number",
            "registration_place",
            "valid_from",
            "expired",
            "is_valid",
            "days_until_expiry",
        ]

    def get_days_until_expiry(self, obj: Insurance) -> Optional[int]:
        return obj.days_until_expiry

    def validate_citizen_id(self, citizen_id: str) -> str:
        if len(citizen_id) != 12:
            raise serializers.ValidationError("Số CCCD phải có đúng 12 số")
        if not citizen_id.isdigit():
            raise serializers.ValidationError("Số CCCD chỉ chứa số")
        return citizen_id

    def validate_phone_number(self, phone_number: str) -> str:
        # Loại bỏ khoảng trắng và dấu gạch ngang
        phone_number = phone_number.replace(" ", "").replace("-", "")
        if not phone_number.isdigit():
            raise serializers.ValidationError("Số điện thoại chỉ chứa số")
        if len(phone_number) != 10:
            raise serializers.ValidationError("Số điện thoại phải có 10 số")

        return phone_number

    def validate_insurance_id(self, insurance_id: str) -> str:
        # Số thẻ BHYT thường có format: XX1234567890123 (15 ký tự)
        if len(insurance_id) < 10:
            raise serializers.ValidationError("Số thẻ BHYT không hợp lệ")
        return insurance_id.upper()

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        valid_from = data.get("valid_from")
        expired = data.get("expired")
        dob = data.get("dob")
        # Kiểm tra ngày sinh
        if dob and dob > date.today():
            raise serializers.ValidationError(
                {"dob": "Ngày sinh không được lớn hơn ngày hiện tại"}
            )
        # Kiểm tra ngày hết hạn
        if expired and expired < date.today():
            raise serializers.ValidationError({"expired": "Ngày hết hạn đã qua"})
        # Kiểm tra valid_from < expired
        if valid_from and expired and valid_from >= expired:
            raise serializers.ValidationError(
                {"valid_from": "Ngày bắt đầu phải nhỏ hơn ngày hết hạn"}
            )
        return data

class InsuranceListSerializer(serializers.ModelSerializer):
    days_until_expiry = serializers.ReadOnlyField()
    dob = serializers.DateField(format="%d/%m/%Y")
    valid_from = serializers.DateField(format="%d/%m/%Y")
    expired = serializers.DateField(format="%d/%m/%Y")

    class Meta:
        model = Insurance
        fields = [
            "insurance_id",
            "citizen_id",
            "fullname",
            "gender",
            "dob",
            "phone_number",
            "registration_place",
            "valid_from",
            "expired",
            "is_valid",
            "days_until_expiry",
        ]

from django.db import transaction
from django.utils.timezone import localdate
from django.db.models import Max

class OrderSerializer(serializers.ModelSerializer):
    citizen_name = serializers.CharField(source='citizen.fullname', read_only=True)
    clinic_service_name = serializers.CharField(source='clinic_service.name', read_only=True)
    order_number = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'queue_number', 'citizen', 'citizen_name', 'clinic_service', 'clinic_service_name',
            'created_at', 'order_status', 'payment_method', 'payment_status', 'prices', 'order_number'
        ]
        read_only_fields = ['id', 'created_at', 'order_number']

    def create(self, validated_data):
        # Sử dụng service để tạo order
        clinic_service = validated_data.get('clinic_service')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            
            # queue_number chưa có thì tính theo số thứ tự tăng dần cho dịch vụ trong ngày
            if not order.queue_number is None and clinic_service:
                today = localdate().today()
                last_order = (Order.objects.filter(clinic_service = clinic_service,created_at__date=today)
                    .aggregate(max_queue_number=Max("queue_number"))
                    .get("max_queue_number"))
                order.queue_number = (last_order or 0) + 1
                order.save(update_fields=["queue_number"])
        return order
    

class PatientSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField(help_text="Tuổi tính tự động")

    class Meta:
        model = Patients
        fields = [
            "citizen_id",
            "fullname",
            "dob",
            "age",
            "gender",
            "phone_number",
            "address",
            "occupation",
            "is_insurance",
            "ethnicity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at", "age")

    def validate_citizen_id(self, citizen_id: str) -> str:
        if not citizen_id.isdigit():
            raise serializers.ValidationError("CCCD phải là số")
        if len(citizen_id) not in [9, 12]:
            raise serializers.ValidationError("CCCD phải 12 số")
        return citizen_id

    def validate_dob(self, dob: date) -> date:
        if dob > date.today():
            raise serializers.ValidationError(
                "Ngày sinh không thể lớn hơn ngày hiện tại"
            )

        age = date.today().year - dob.year
        if age > 150:
            raise serializers.ValidationError("Tuổi không hợp lệ")

        return dob


class PatientListSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = Patients
        fields = [
            "citizen_id",
            "fullname",
            "dob",
            "age",
            "address",
            "gender",
            "phone_number",
            "is_insurance",
            "ethnicity",
            "occupation",
        ]
        read_only_fields = ("citizen_id", "age")


class PatientDetailSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = Patients
        fields = "__all__"
        read_only_fields = ("citizen_id", "created_at", "updated_at", "age")


class ServiceExamCreateSerializer(serializers.Serializer):
    service_name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    price_insurance = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_non_insurance = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data: dict[str, Any]) -> ServiceExam:
        return ServiceExam.objects.create(
            name=validated_data["service_name"],
            description=validated_data.get("description", ""),
            prices_insurance=validated_data["price_insurance"],
            prices_non_insurance=validated_data["price_non_insurance"],
        )


class ServiceExamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceExam
        # Chỉ lấy các fields quan trọng
        fields = [
            "id",
            "name",
            "description",
            "prices_insurance",
            "prices_non_insurance",
            "is_active",
        ]

class ServiceExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceExam
        fields = ["name", "description", "prices_insurance", "prices_non_insurance"]

class ServiceExamDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceExam
        # Lấy tất cả các fields của model
        fields = "__all__"

from apps.kiosk.models import CustomUser
from django.contrib.auth import get_user_model
# Lấy CustomUser model (đã config trong settings.AUTH_USER_MODEL)
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # Custom fields (computed fields)
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)

    class Meta:
        model = User
        fields = [
            # Basic info (từ AbstractUser)
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",  # Computed field
            # Contact info
            "phone",
            "address",
            # Work info
            "role",
            "role_display",  # Human-readable role
            "department",
            "employee_id",
            # Personal info
            "avatar",
            "dob",
            "gender",
            "gender_display",  # Human-readable gender
            # Status & metadata
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "updated_at",
            # Additional
            "notes",
        ]

        read_only_fields = [
            "id",
            "date_joined",
            "last_login",
            "updated_at",
            "full_name",
            "role_display",
            "gender_display",
        ]

    def get_full_name(self, obj: "CustomUser") -> str:
        return obj.full_name


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "role",
            "role_display",
            "department",
            "employee_id",
            "phone",
            "is_active",
            "is_staff",
        ]

    def get_full_name(self, obj: "CustomUser") -> str:
        return obj.full_name


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            # Basic info
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            # Contact info
            "phone",
            "address",
            # Work info
            "role",
            "department",
            "employee_id",
            # Personal info
            "dob",
            "gender",
            # Additional
            "notes",
        ]

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError({"password2": "Mật khẩu không khớp"})
        return data

    def validate_employee_id(self, value: str) -> str:
        if value and User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Mã nhân viên đã tồn tại")
        return value

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email đã được sử dụng")
        return value

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username đã tồn tại")
        return value

    def create(self, validated_data: dict[str, Any]) -> User:
        validated_data.pop("password2")
        password = validated_data.pop("password")

        # Tạo user với tất cả fields
        user = User.objects.create(**validated_data)
        # Hash password (KHÔNG lưu plain text)
        user.set_password(password)
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            # Basic info
            "email",
            "first_name",
            "last_name",
            # Contact info
            "phone",
            "address",
            # Work info
            "role",
            "department",
            "employee_id",
            # Personal info
            "avatar",
            "dob",
            "gender",
            # Status
            "is_active",
            # Additional
            "notes",
        ]

    def validate_email(self, value: str) -> str:
        user = self.instance
        if user and User.objects.exclude(pk=user.pk).filter(email=value).exists():  # type: ignore
            raise serializers.ValidationError("Email đã được sử dụng")
        return value

    def validate_employee_id(self, value: str) -> str:
        user = self.instance
        if (
            value
            and user
            and User.objects.exclude(pk=user.pk).filter(employee_id=value).exists()  # type: ignore
        ):
            raise serializers.ValidationError("Mã nhân viên đã tồn tại")
        return value
