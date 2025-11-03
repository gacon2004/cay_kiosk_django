"""
MODEL LAYER - Insurance Model
Quản lý thông tin bảo hiểm y tế
"""

from django.db import models
from .patient import Patients


class Insurance(models.Model):
    """Model bảo hiểm y tế - Lưu trữ thông tin BHYT của bệnh nhân"""

    patient_id = models.ForeignKey(
        Patients,
        on_delete=models.CASCADE,
        related_name="insurances",
        verbose_name="Bệnh nhân",
    )
    insurance_number = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Số thẻ BHYT",
        help_text="Mã số thẻ bảo hiểm y tế",
    )
    expiry_date = models.DateField(verbose_name="Ngày hết hạn")
    issued_date = models.DateField(verbose_name="Ngày cấp", null=True, blank=True)
    insurance_type = models.CharField(
        max_length=50,
        verbose_name="Loại bảo hiểm",
        default="BHYT",
        help_text="Loại bảo hiểm: BHYT, BHTN, ...",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Bảo hiểm y tế"
        verbose_name_plural = "Bảo hiểm y tế"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["insurance_number"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self):
        return f"{self.insurance_number} - {self.patient_id.full_name}"

    @property
    def is_valid(self):
        """Kiểm tra thẻ BHYT còn hiệu lực không"""
        from datetime import date

        return self.expiry_date >= date.today()

    def days_until_expiry(self):
        """Số ngày còn lại đến khi hết hạn"""
        from datetime import date

        delta = self.expiry_date - date.today()
        return delta.days
