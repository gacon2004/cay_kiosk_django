"""
MODEL LAYER - Patient Model
Quản lý thông tin bệnh nhân
"""

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from datetime import date

# Migration là "lịch sử thay đổi database" - giống như Git cho database
# python manage.py makemigrations  # Tạo file migration này
# python manage.py migrate         # Áp dụng vào database
# Django sẽ đọc file này và tạo các bảng trong database theo đúng cấu trúc đã định nghĩa.
class Patients(models.Model):
    """Model bệnh nhân - Lưu trữ thông tin cá nhân bệnh nhân"""

    GENDER_CHOICES = [
        ("Nam", "Nam"),
        ("Nữ", "Nữ"),
        ("Khác", "Khác"),
    ]

    national_id = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="CMND/CCCD",
        help_text="Số căn cước công dân",
    )
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    date_of_birth = models.DateField(verbose_name="Ngày sinh")
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, verbose_name="Giới tính"
    )
    phone = PhoneNumberField(region="VN", verbose_name="Số điện thoại")
    address = models.CharField(
        max_length=100, verbose_name="Địa chỉ", blank=True, null=True
    )
    occupation = models.CharField(
        max_length=100, verbose_name="Nghề nghiệp", blank=True, null=True
    )
    ethnicity = models.CharField(max_length=50, verbose_name="Dân tộc", default="Kinh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Bệnh nhân"
        verbose_name_plural = "Bệnh nhân"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["national_id"]),
            models.Index(fields=["full_name"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.national_id}"
    
    @property
    def age(self):
        """Tính tuổi bệnh nhân"""
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )
