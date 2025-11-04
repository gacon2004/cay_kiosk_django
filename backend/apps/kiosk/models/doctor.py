"""
MODEL LAYER - Doctor Model
Quản lý thông tin bác sĩ
"""

from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField


class Doctors(models.Model):
    """Model bác sĩ - Lưu trữ thông tin bác sĩ"""

    doctor_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Mã bác sĩ",
        help_text="Mã định danh bác sĩ",
    )
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    specialization = models.CharField(
        max_length=100,
        verbose_name="Chuyên khoa",
        help_text="Ví dụ: Tim mạch, Nội khoa, Ngoại khoa...",
    )
    phone = PhoneNumberField(region="VN", verbose_name="Số điện thoại")
    email = models.EmailField(verbose_name="Email", unique=True)
    user_id = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ Dùng settings thay vì get_user_model()
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_profile",
        verbose_name="Tài khoản người dùng",
    )
    years_of_experience = models.PositiveIntegerField(
        verbose_name="Số năm kinh nghiệm", default=0
    )
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Bác sĩ"
        verbose_name_plural = "Bác sĩ"
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["doctor_id"]),
            models.Index(fields=["specialization"]),
        ]

    def __str__(self):
        return f"BS. {self.full_name} - {self.specialization}"

    @property
    def title(self):
        """Trả về danh xưng với tên"""
        return f"BS. {self.full_name}"
