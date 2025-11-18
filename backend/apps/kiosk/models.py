"""
LEGACY FILE - Deprecated
Sử dụng models từ thư mục models/ theo cấu trúc MVC mới
File này chỉ để backward compatibility
"""

from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser

class Clinic(models.Model):
    # ID tự động tăng (Django tự tạo, không cần khai báo)
    # id = models.AutoField(primary_key=True)  # Có thể bỏ qua vì Django tự tạo
    name = models.CharField(max_length=200, verbose_name="Tên phòng khám")
    is_active = models.BooleanField(default=True, verbose_name="Trạng thái")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        # Tên bảng trong database
        db_table = "clinics"
        # Tên hiển thị trong Django Admin
        verbose_name = "Phòng khám"
        verbose_name_plural = "Phòng khám"
        # Sắp xếp theo tên phòng (A-Z)
        ordering = ["name"]
        # Index để tăng tốc độ query
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        #String representation của object
        #Hiển thị tên phòng khám khi print(clinic)
        return self.name

    def activate(self):
        # Method để kích hoạt phòng khám
        self.is_active = True
        self.save()

    def deactivate(self):
        """
        Method để vô hiệu hóa phòng khám
        """
        self.is_active = False
        self.save()

class Doctors(models.Model):
    doctor_id = models.CharField(max_length=20,unique=True,verbose_name="Mã bác sĩ")
    fullname = models.CharField(max_length=100, verbose_name="Họ và tên")
    specialization = models.CharField(max_length=100, verbose_name="Chuyên khoa")
    phone_number = PhoneNumberField(region="VN", verbose_name="Số điện thoại")
    email = models.EmailField(verbose_name="Email", unique=True)
    user_id = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Dùng settings thay vì get_user_model()
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_profile",
        verbose_name="Tài khoản người dùng",
    )
    years_of_experience = models.PositiveIntegerField( default=0, verbose_name="Năm kinh nghiệm")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:  # tùy chỉnh
        verbose_name = "Bác sĩ"
        verbose_name_plural = "Bác sĩ"
        ordering = ["fullname"]
        indexes = [
            models.Index(fields=["doctor_id"]),
            models.Index(fields=["specialization"]),
        ]

    def __str__(self):
        return f"BS. {self.fullname} - {self.specialization}"

    @property
    def title(self):
        #Trả về danh xưng với tên
        return f"BS. {self.fullname}"

from datetime import date
class Insurance(models.Model):
    
    
    citizen_id = models.CharField(max_length=12,primary_key=True,verbose_name="Số CCCD")
    insurance_id = models.CharField(max_length=12,unique=True,verbose_name="Mã thẻ BHYT")
    fullname = models.CharField(max_length=100, verbose_name="Họ và tên")
    gender = models.BooleanField(choices=[(1, "Nam"), (0, "Nữ")],verbose_name="Giới tính")
    dob = models.DateField(verbose_name="Ngày sinh")
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại")
    registration_place = models.CharField(max_length=255, verbose_name="Nơi đăng ký KCB")
    valid_from = models.DateField(verbose_name="Ngày bắt đầu hiệu lực")
    expired = models.DateField(verbose_name="Ngày hết hạn")

    class Meta:
        verbose_name = "Bảo hiểm y tế"
        verbose_name_plural = "Bảo hiểm y tế"
        ordering = ["-expired"]
        indexes = [
            models.Index(fields=["insurance_id"]),
            models.Index(fields=["expired"]),
        ]

    def __str__(self):
        return f"{self.fullname} - {self.insurance_id}"

    @property
    def is_valid(self):
        today = date.today()
        return self.valid_from <= today <= self.expired

    @property
    def is_expired(self):
        return self.expired < date.today()

    @property
    def days_until_expiry(self):
        delta = self.expired - date.today()
        return delta.days

    @property
    def gender_display(self):
        return "Nam" if self.gender == 1 else "Nữ"

    @property
    def age(self):
        today = date.today()
        return (today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day)))

    @property
    def coverage_period(self):
        return f"{self.valid_from.strftime('%d/%m/%Y')} - {self.expired.strftime('%d/%m/%Y')}"

    @classmethod
    def check_insurance_exists(cls, citizen_id):
        return cls.objects.filter(citizen_id=citizen_id).exists()

    @classmethod
    def get_by_citizen_id(cls, citizen_id):
        try:
            return cls.objects.get(citizen_id=citizen_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_insurance_id(cls, insurance_id):
        try:
            return cls.objects.get(insurance_id=insurance_id)
        except cls.DoesNotExist:
            return None

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("pending", "Chờ xử lý"),
        ("confirmed", "Đã xác nhận"),
        ("in_progress", "Đang thực hiện"),
        ("completed", "Hoàn thành"),
        ("cancelled", "Đã hủy"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Tiền mặt"),
        ("card", "Thẻ tín dụng"),
        ("transfer", "Chuyển khoản"),
        ("insurance", "Bảo hiểm"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Chưa thanh toán"),
        ("paid", "Đã thanh toán"),
        ("refunded", "Đã hoàn tiền"),
    ]

    # Có thể sử dụng id này hoặc tạo order_number riêng nếu cần
    id = models.AutoField(primary_key=True)
    queue_number = models.PositiveIntegerField(verbose_name="Số thứ tự", help_text="Số thứ tự trong hàng đợi",blank=True,null=True)
    citizen = models.ForeignKey("Patients",on_delete=models.CASCADE,verbose_name="Bệnh nhân",related_name="orders")
    clinic_service = models.ForeignKey("ServiceExam",on_delete=models.CASCADE,verbose_name="Dịch vụ khám",related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Thời gian tạo")
    order_status = models.CharField(max_length=20,choices=ORDER_STATUS_CHOICES,default="pending",verbose_name="Trạng thái đơn hàng")
    payment_method = models.CharField(max_length=20,choices=PAYMENT_METHOD_CHOICES,blank=True,null=True,verbose_name="Phương thức thanh toán")
    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS_CHOICES,default="unpaid",verbose_name="Trạng thái thanh toán")
    prices = models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Giá tiền",blank=True,null=True)
    queue_number = models.PositiveIntegerField(auto_created=True, verbose_name="Số thứ tự trong ngày", null=True, blank=True)
    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["citizen"]),
            models.Index(fields=["clinic_service"]),
            models.Index(fields=["order_status"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.citizen.fullname} - {self.clinic_service.name}"

    @property
    def order_number(self):
        return f"ORD{self.id:06d}"

    def save(self, *args, **kwargs):
        #Tự động tính giá dựa trên dịch vụ và bảo hiểm
        if not self.prices and self.clinic_service:
            if self.citizen.is_insurance:
                self.prices = self.clinic_service.prices_insurance
            else:
                self.prices = self.clinic_service.prices_non_insurance
        super().save(*args, **kwargs)
    

# Migration là "lịch sử thay đổi database" - giống như Git cho database
# python manage.py makemigrations  # Tạo file migration này
# python manage.py migrate         # Áp dụng vào database
# Django sẽ đọc file này và tạo các bảng trong database theo đúng cấu trúc đã định nghĩa.
class Patients(models.Model):
    citizen_id = models.CharField(max_length=12,unique=True,verbose_name="CMND/CCCD",help_text="Số căn cước công dân",primary_key=True)
    fullname = models.CharField(max_length=100, verbose_name="Họ và tên")
    dob = models.DateField(verbose_name="Ngày sinh")
    gender = models.BooleanField(choices=[(True, "Nam"), (False, "Nữ")], verbose_name="Giới tính")
    phone_number = PhoneNumberField(region="VN", verbose_name="Số điện thoại")
    address = models.CharField(max_length=100, verbose_name="Địa chỉ", blank=True, null=True)
    occupation = models.CharField(max_length=100, verbose_name="Nghề nghiệp", blank=True, null=True)
    is_insurance = models.BooleanField(verbose_name="Có bảo hiểm", default=False)
    ethnicity = models.CharField(max_length=50, verbose_name="Dân tộc", default="Kinh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Bệnh nhân"
        verbose_name_plural = "Bệnh nhân"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["citizen_id"]),
            models.Index(fields=["fullname"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.fullname} - {self.citizen_id}"

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

class ServiceExam(models.Model):
    # ID tự động tăng (Django tự tạo, không cần khai báo)
    # id = models.AutoField(primary_key=True)  # Có thể bỏ qua vì Django tự tạo
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    prices_non_insurance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá dịch vụ không bảo hiểm")
    prices_insurance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá dịch vụ có bảo hiểm")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} - {'Hoạt động' if self.is_active else 'Ngừng hoạt động'} - Giá (KHÔNG BHYT): {self.prices_non_insurance} - Giá (CÓ BHYT): {self.prices_insurance}"




class CustomUser(AbstractUser):
    """
    Custom User Model kế thừa AbstractUser

    Kế thừa tất cả fields từ AbstractUser:
    - username, password, email, first_name, last_name
    - is_active, is_staff, is_superuser
    - date_joined, last_login
    """
    phone = models.CharField(max_length=20,blank=True,null=True,verbose_name="Số điện thoại")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ", help_text="Địa chỉ chi tiết")

    ROLE_CHOICES = [
        ("admin", "Quản trị viên"),
        ("doctor", "Bác sĩ"),
        ("nurse", "Y tá"),
        ("receptionist", "Lễ tân"),
        ("accountant", "Kế toán"),
        ("pharmacist", "Dược sĩ"),
        ("technician", "Kỹ thuật viên"),
    ]

    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default="receptionist",verbose_name="Vai trò")
    department = models.CharField(max_length=100,blank=True,null=True,verbose_name="Khoa/Phòng ban")
    employee_id = models.CharField(max_length=20,unique=True,blank=True,null=True,verbose_name="Mã nhân viên")
    dob = models.DateField(blank=True,null=True,verbose_name="Ngày sinh")
    gender = models.BooleanField(choices=[(True, "Nam"), (False, "Nữ")], verbose_name="Giới tính")
    created_by = models.ForeignKey("self",on_delete=models.SET_NULL,null=True,blank=True,related_name="created_users",verbose_name="Người tạo")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    notes = models.TextField(blank=True,null=True,verbose_name="Ghi chú")

    class Meta:
        app_label = "kiosk"  # Explicitly set app_label
        db_table = "custom_users"
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["employee_id"]),
            models.Index(fields=["role"]),
            models.Index(fields=["department"]),
        ]

    def __str__(self):
        role_display = dict(self.ROLE_CHOICES).get(self.role, self.role)
        return f"{self.full_name} ({role_display})"

    @property
    def full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.username

    def get_short_name(self):
        return self.first_name or self.username

    @property
    def is_doctor(self):
        return self.role == "doctor"

    @property
    def is_nurse(self):
        return self.role == "nurse"

    @property
    def is_admin_role(self):
        return self.role == "admin"

