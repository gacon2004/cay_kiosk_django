"""
MODEL LAYER - Bank Information Model
Quản lý thông tin ngân hàng
"""
from django.db import models


class BankInformation(models.Model):
    """Model thông tin ngân hàng - Lưu trữ thông tin tài khoản ngân hàng"""
    
    bank_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Mã ngân hàng",
        help_text="Mã định danh tài khoản ngân hàng"
    )
    bank_name = models.CharField(
        max_length=100,
        verbose_name="Tên ngân hàng",
        help_text="Ví dụ: Vietcombank, BIDV, Techcombank..."
    )
    account_number = models.CharField(
        max_length=30,
        verbose_name="Số tài khoản"
    )
    account_holder = models.CharField(
        max_length=100,
        verbose_name="Tên chủ tài khoản",
        blank=True
    )
    branch = models.CharField(
        max_length=100,
        verbose_name="Chi nhánh",
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )

    class Meta:
        verbose_name = "Thông tin ngân hàng"
        verbose_name_plural = "Thông tin ngân hàng"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bank_id']),
            models.Index(fields=['account_number']),
        ]

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"
    
    def get_masked_account_number(self):
        """Trả về số tài khoản đã che (**** xxxx 1234)"""
        if len(self.account_number) > 4:
            return f"**** **** {self.account_number[-4:]}"
        return self.account_number
