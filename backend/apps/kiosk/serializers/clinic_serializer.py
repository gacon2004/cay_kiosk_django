"""
VIEW LAYER (Serializers) - Clinic Serializer
Serializers cho Clinic model
"""

from typing import Any
from rest_framework import serializers
from apps.kiosk.models import Clinic


class ClinicSerializer(serializers.ModelSerializer):
    """
    Serializer đầy đủ cho Clinic
    Sử dụng cho detail view và create/update operations
    """

    class Meta:
        # Model để serialize
        model = Clinic
        # Tất cả các fields sẽ được trả về
        fields = [
            "id",  # ID tự động tăng
            "name",  # Tên phòng khám
            "is_active",  # Trạng thái (True/False)
            "address",  # Địa chỉ
            "created_at",  # Ngày tạo
            "updated_at",  # Ngày cập nhật
        ]
        # Các fields chỉ đọc, không cho phép client cập nhật
        read_only_fields = ["id", "created_at", "updated_at", "is_active"]

    def validate_name(self, name_clinic: str) -> str:
        """
        Validate tên phòng khám không được trống hoặc chỉ có khoảng trắng
        Args:
            value: Tên phòng khám cần validate
        Returns:
            str: Tên phòng khám đã được strip
        Raises:
            ValidationError: Nếu tên không hợp lệ
        """
        # Strip khoảng trắng đầu cuối
        name_clinic = name_clinic.strip()
        # Kiểm tra tên có rỗng không
        if not name_clinic:
            raise serializers.ValidationError("Tên phòng khám không được để trống")
        # Kiểm tra độ dài tối thiểu
        if len(name_clinic) < 3:
            raise serializers.ValidationError("Tên phòng khám phải có ít nhất 3 ký tự")
        return name_clinic


class ClinicListSerializer(serializers.ModelSerializer):
    """
    Serializer rút gọn cho danh sách phòng khám
    Chỉ trả về các fields cần thiết cho list view
    Giúp giảm dung lượng response
    """
    class Meta:
        model = Clinic
        # Chỉ lấy các fields quan trọng
        fields = ["name", "is_active", "address"]

class ClinicCreateSerializer(serializers.ModelSerializer):
    """
    Serializer cho tạo phòng khám mới
    Validate các trường bắt buộc
    """

    class Meta:  # cấu hình riêng biệt
        model = Clinic  # model để serialize
        # Các fields cần thiết khi tạo mới
        fields = ["name", "address", "is_active"]

    def validate_name(self, value: str) -> str:
        """
        Validate tên phòng khám
        Kiểm tra tên không trùng (case-insensitive)
        Args:
            value: Tên phòng khám cần validate
        Returns:
            str: Tên phòng khám đã được strip
        Raises:
            ValidationError: Nếu tên trống hoặc đã tồn tại
        """
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên phòng khám không được để trống")

        # Kiểm tra tên đã tồn tại chưa (không phân biệt hoa thường)
        if Clinic.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Tên phòng khám đã tồn tại")

        return value


class ClinicUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer cho cập nhật phòng khám
    """

    class Meta:
        model = Clinic
        # Các fields có thể update
        fields = ["name", "address", "is_active"]

    def validate_name(self, value: str) -> str:
        """
        Validate tên phòng khám khi update
        Kiểm tra tên không trùng với phòng khác (trừ chính nó)
        Args:
            value: Tên phòng khám cần validate
        Returns:
            str: Tên phòng khám đã được strip
        Raises:
            ValidationError: Nếu tên trống hoặc trùng với phòng khác
        """
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên phòng khám không được để trống")

        # Lấy instance đang được update
        clinic = self.instance
        # Kiểm tra tên đã tồn tại chưa (loại trừ chính nó)
        if Clinic.objects.exclude(pk=clinic.pk).filter(name__iexact=value).exists():
            raise serializers.ValidationError("Tên phòng khám đã tồn tại")

        return value
