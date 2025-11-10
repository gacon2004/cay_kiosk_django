"""
MODEL LAYER - Custom User Model
Mở rộng Django User với các fields bổ sung cho Healthcare Kiosk
"""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User Model kế thừa AbstractUser

    Kế thừa tất cả fields từ AbstractUser:
    - username, password, email, first_name, last_name
    - is_active, is_staff, is_superuser
    - date_joined, last_login

    Thêm các fields bổ sung cho hệ thống Healthcare Kiosk
    """

    # ============= THÔNG TIN LIÊN HỆ =============

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Số điện thoại",
        help_text="Số điện thoại liên hệ",
    )

    address = models.TextField(
        blank=True, null=True, verbose_name="Địa chỉ", help_text="Địa chỉ chi tiết"
    )

    # ============= THÔNG TIN CÔNG VIỆC =============

    ROLE_CHOICES = [
        ("admin", "Quản trị viên"),
        ("doctor", "Bác sĩ"),
        ("nurse", "Y tá"),
        ("receptionist", "Lễ tân"),
        ("accountant", "Kế toán"),
        ("pharmacist", "Dược sĩ"),
        ("technician", "Kỹ thuật viên"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="receptionist",
        verbose_name="Vai trò",
        help_text="Vai trò của người dùng trong hệ thống",
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Khoa/Phòng ban",
        help_text="Ví dụ: Khoa Nội, Khoa Ngoại, Phòng Kế toán...",
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Mã nhân viên",
        help_text="Mã nhân viên duy nhất (VD: NV001, BS123...)",
    )

    # ============= THÔNG TIN BỔ SUNG =============

    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Ảnh đại diện",
        help_text="Ảnh đại diện của người dùng",
    )

    dob = models.DateField(
        blank=True,
        null=True,
        verbose_name="Ngày sinh",
        help_text="Ngày sinh của người dùng",
    )

    gender = models.BooleanField(
        choices=[(True, "Nam"), (False, "Nữ")], verbose_name="Giới tính"
    )

    # ============= METADATA =============

    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users",
        verbose_name="Người tạo",
        help_text="Người dùng đã tạo tài khoản này",
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú",
        help_text="Ghi chú thêm về người dùng",
    )

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
        """String representation"""
        role_display = dict(self.ROLE_CHOICES).get(self.role, self.role)
        return f"{self.full_name} ({role_display})"

    @property
    def full_name(self):
        """
        Trả về họ tên đầy đủ
        Nếu không có first_name/last_name thì return username
        """
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.username

    def get_short_name(self):
        """Override method từ AbstractUser"""
        return self.first_name or self.username

    @property
    def is_doctor(self):
        """Check xem có phải bác sĩ không"""
        return self.role == "doctor"

    @property
    def is_nurse(self):
        """Check xem có phải y tá không"""
        return self.role == "nurse"

    @property
    def is_admin_role(self):
        """Check xem có phải admin không (khác với is_superuser)"""
        return self.role == "admin"


# Giữ lại alias cũ để backward compatible (tạm thời)
# Sau khi migrate xong có thể xóa
Users = CustomUser
