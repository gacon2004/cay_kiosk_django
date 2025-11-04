import django.db.models as models


class ServiceExam(models.Model):
    """Model dịch vụ khám bệnh - Lưu trữ thông tin về các dịch vụ khám bệnh"""

    # ID tự động tăng (Django tự tạo, không cần khai báo)
    # id = models.AutoField(primary_key=True)  # Có thể bỏ qua vì Django tự tạo
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    prices_non_insurance = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Giá dịch vụ không bảo hiểm"
    )
    prices_insurance = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Giá dịch vụ có bảo hiểm"
    )

    def __str__(self):
        return f"{self.name} - {'Hoạt động' if self.is_active else 'Ngừng hoạt động'} - Giá (KHÔNG BHYT): {self.prices_non_insurance} - Giá (CÓ BHYT): {self.prices_insurance}"
