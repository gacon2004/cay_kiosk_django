"""
MODEL LAYER - Clinic Model
Quản lý thông tin phòng khám
"""

from django.db import models


class Clinic(models.Model):
    """
    Model Phòng khám
    Lưu trữ thông tin các phòng khám trong bệnh viện/cơ sở y tế
    """
    
    # ID tự động tăng (Django tự tạo, không cần khai báo)
    # id = models.AutoField(primary_key=True)  # Có thể bỏ qua vì Django tự tạo
    
    # Tên phòng khám (bắt buộc, tối đa 200 ký tự)
    name = models.CharField(
        max_length=200,
        verbose_name="Tên phòng khám",
        help_text="Tên đầy đủ của phòng khám"
    )
    
    # Trạng thái phòng khám (True = Hoạt động, False = Ngừng hoạt động)
    is_active = models.BooleanField(
        default=True,
        verbose_name="Trạng thái",
        help_text="Phòng khám có đang hoạt động không"
    )
    
    # Địa chỉ phòng khám (có thể để trống)
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Địa chỉ",
        help_text="Địa chỉ chi tiết của phòng khám"
    )
    
    # Thời gian tạo (tự động lưu khi tạo mới)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    # Thời gian cập nhật (tự động cập nhật mỗi khi save)
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )
    
    class Meta:
        # Tên bảng trong database
        db_table = 'clinics'
        # Tên hiển thị trong Django Admin
        verbose_name = 'Phòng khám'
        verbose_name_plural = 'Phòng khám'
        # Sắp xếp theo tên phòng (A-Z)
        ordering = ['name']
        # Index để tăng tốc độ query
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        """
        String representation của object
        Hiển thị tên phòng khám khi print(clinic)
        """
        return self.name
    
    def activate(self):
        """
        Method để kích hoạt phòng khám
        """
        self.is_active = True
        self.save()
    
    def deactivate(self):
        """
        Method để vô hiệu hóa phòng khám
        """
        self.is_active = False
        self.save()
