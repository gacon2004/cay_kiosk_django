"""
MODEL LAYER - Insurance Model
Hệ thống quản lý thông tin bảo hiểm y tế (dữ liệu từ hệ thống bên ngoài)
Người dùng kiểm tra xem bảo hiểm có tồn tại và còn hiệu lực không
"""

from datetime import date

from django.db import models


class Insurance(models.Model):
    """
    Model bảo hiểm y tế - Dữ liệu từ hệ thống BHYT bên ngoài
    Cấu trúc: citizen_id, insurance_id, fullname, gender, dob, phone_number,
              registration_place, valid_from, expired
    """

    # citizen_id - CCCD (Primary key)
    citizen_id = models.CharField(
        max_length=12,
        primary_key=True,
        verbose_name="Số CCCD",
        help_text="Số căn cước công dân",
    )

    # insurance_id - Mã thẻ BHYT
    insurance_id = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="Mã thẻ BHYT",
        help_text="Mã số thẻ bảo hiểm y tế",
    )

    # fullname - Họ tên
    fullname = models.CharField(
        max_length=100,
        verbose_name="Họ và tên",
    )

    # gender - Giới tính
    gender = models.BooleanField(
        choices=[(1, "Nam"), (0, "Nữ")],
        verbose_name="Giới tính",
    )

    # dob - Ngày sinh
    dob = models.DateField(
        verbose_name="Ngày sinh",
    )

    # phone_number - Số điện thoại
    phone_number = models.CharField(
        max_length=15,
        verbose_name="Số điện thoại",
    )

    # registration_place - Nơi đăng ký KCB
    registration_place = models.CharField(
        max_length=255,
        verbose_name="Nơi đăng ký KCB",
        help_text="Bệnh viện đăng ký khám chữa bệnh ban đầu",
    )

    # valid_from - Ngày có hiệu lực
    valid_from = models.DateField(
        verbose_name="Ngày bắt đầu hiệu lực",
    )

    # expired - Ngày hết hạn
    expired = models.DateField(
        verbose_name="Ngày hết hạn",
    )

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
        """Kiểm tra thẻ BHYT còn hiệu lực không"""
        today = date.today()
        # Kiểm tra trong khoảng thời gian hiệu lực
        return self.valid_from <= today <= self.expired

    @property
    def is_expired(self):
        """Kiểm tra thẻ đã hết hạn chưa"""
        return self.expired < date.today()

    @property
    def days_until_expiry(self):
        """Số ngày còn lại đến khi hết hạn"""
        delta = self.expired - date.today()
        return delta.days

    @property
    def gender_display(self):
        """Hiển thị giới tính dạng text"""
        return "Nam" if self.gender == 1 else "Nữ"

    @property
    def age(self):
        """Tính tuổi từ ngày sinh"""
        today = date.today()
        return (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    @property
    def coverage_period(self):
        """Khoảng thời gian bảo hiểm"""
        return f"{self.valid_from.strftime('%d/%m/%Y')} - {self.expired.strftime('%d/%m/%Y')}"

    @classmethod
    def check_insurance_exists(cls, citizen_id):
        """Kiểm tra bảo hiểm có tồn tại không"""
        return cls.objects.filter(citizen_id=citizen_id).exists()

    @classmethod
    def get_by_citizen_id(cls, citizen_id):
        """Lấy thông tin bảo hiểm theo CCCD"""
        try:
            return cls.objects.get(citizen_id=citizen_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_insurance_id(cls, insurance_id):
        """Lấy thông tin bảo hiểm theo mã thẻ BHYT"""
        try:
            return cls.objects.get(insurance_id=insurance_id)
        except cls.DoesNotExist:
            return None
            return None
