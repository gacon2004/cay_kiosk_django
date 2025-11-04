"""
SERVICE LAYER - Clinic Service
Xử lý business logic liên quan đến phòng khám
Tách biệt business logic khỏi views để dễ test và maintain
"""
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from apps.kiosk.models import Clinic


class ClinicService:
    """
    Service class xử lý business logic cho phòng khám
    """
    @staticmethod
    def get_all_clinics(
        is_active: Optional[bool] = None, search: Optional[str] = None
    ) -> QuerySet[Clinic]:
        """
        Lấy danh sách phòng khám với filter và search
        Args:
            is_active: Lọc theo trạng thái hoạt động (True/False/None)
            search: Tìm kiếm theo tên phòng khám
        Returns:
            QuerySet[Clinic]: Danh sách phòng khám
        """
        queryset = Clinic.objects.all().order_by("name")
        # Filter theo trạng thái
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        # Search theo tên
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    @staticmethod
    def get_clinic_by_id(clinic_id: int) -> Clinic:
        """
        Lấy thông tin chi tiết một phòng khám
        Args:
            clinic_id: ID phòng khám
        Returns:
            Clinic: Instance phòng khám
        Raises:
            ValidationError: Nếu không tìm thấy phòng khám
        """
        try:
            return Clinic.objects.get(id=clinic_id)
        except Clinic.DoesNotExist:
            raise ValidationError(f"Không tìm thấy phòng khám với ID {clinic_id}")

    @staticmethod
    @transaction.atomic
    def create_clinic(clinic_data: Dict[str, Any]) -> Clinic:
        """
        Tạo phòng khám mới với validation
        Args:
            clinic_data: Dữ liệu phòng khám
                {
                    "name": str (required) - Tên phòng khám,
                    "address": str (optional) - Địa chỉ,
                    "is_active": bool (optional) - Trạng thái (default: True)
                }
        Returns:
            Clinic: Phòng khám vừa tạo
        Raises:
            ValidationError: Nếu dữ liệu không hợp lệ
        """
        # Validate tên không trùng
        name = clinic_data.get("name").strip()
        if Clinic.objects.filter(name__iexact=name).exists():
            raise ValidationError(f"Phòng khám '{name}' đã tồn tại")
        # Tạo phòng khám
        clinic = Clinic.objects.create(**clinic_data)
        return clinic

    @staticmethod
    @transaction.atomic
    def update_clinic(clinic_id: int, update_data: Dict[str, Any]) -> Clinic:
        """
        Cập nhật thông tin phòng khám
        Args:
            clinic_id: ID phòng khám
            update_data: Dữ liệu cần cập nhật
                {
                    "name": str (optional) - Tên phòng khám mới,
                    "address": str (optional) - Địa chỉ mới,
                    "is_active": bool (optional) - Trạng thái mới
                }
        Returns:
            Clinic: Phòng khám đã cập nhật

        Raises:
            ValidationError: Nếu không tìm thấy hoặc dữ liệu không hợp lệ
        """
        clinic = ClinicService.get_clinic_by_id(clinic_id)

        # Validate tên không trùng (nếu update tên)
        new_name = update_data.get("name")
        if new_name:
            new_name = new_name.strip()
            if (
                Clinic.objects.exclude(pk=clinic.pk)
                .filter(name__iexact=new_name)
                .exists()
            ):
                raise ValidationError(f"Phòng khám '{new_name}' đã tồn tại")

        # Cập nhật các fields
        for key, value in update_data.items():
            if hasattr(clinic, key):
                setattr(clinic, key, value)

        clinic.full_clean()  # Validate model
        clinic.save()

        return clinic

    @staticmethod
    @transaction.atomic
    def delete_clinic(clinic_id: int) -> bool:
        """
        Xóa phòng khám

        Args:
            clinic_id: ID phòng khám

        Returns:
            bool: True nếu xóa thành công

        Raises:
            ValidationError: Nếu không tìm thấy phòng khám
        """
        clinic = ClinicService.get_clinic_by_id(clinic_id)
        clinic.delete()
        return True

    @staticmethod
    @transaction.atomic
    def activate_clinic(clinic_id: int) -> Clinic:
        """
        Kích hoạt phòng khám

        Args:
            clinic_id: ID phòng khám

        Returns:
            Clinic: Phòng khám đã kích hoạt
        """
        clinic = ClinicService.get_clinic_by_id(clinic_id)
        clinic.is_active = True
        clinic.save()
        return clinic

    @staticmethod
    @transaction.atomic
    def deactivate_clinic(clinic_id: int) -> Clinic:
        """
        Vô hiệu hóa phòng khám

        Args:
            clinic_id: ID phòng khám

        Returns:
            Clinic: Phòng khám đã vô hiệu hóa
        """
        clinic = ClinicService.get_clinic_by_id(clinic_id)
        clinic.is_active = False
        clinic.save()
        return clinic

    @staticmethod
    def get_active_clinics() -> QuerySet[Clinic]:
        """
        Lấy danh sách phòng khám đang hoạt động

        Returns:
            QuerySet[Clinic]: Danh sách phòng khám active
        """
        return Clinic.objects.filter(is_active=True).order_by("name")

    @staticmethod
    def search_clinics_by_name(query: str) -> QuerySet[Clinic]:
        """
        Tìm kiếm phòng khám theo tên (không phân biệt hoa thường)

        Args:
            query: Từ khóa tìm kiếm

        Returns:
            QuerySet[Clinic]: Danh sách phòng khám khớp với từ khóa
        """
        return Clinic.objects.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        ).order_by("name")

    @staticmethod
    def get_clinic_statistics() -> Dict[str, int]:
        """
        Lấy thống kê tổng quan về phòng khám

        Returns:
            Dict[str, int]: Thống kê
                {
                    "total": int - Tổng số phòng khám,
                    "active": int - Số phòng khám đang hoạt động,
                    "inactive": int - Số phòng khám không hoạt động
                }
        """
        total = Clinic.objects.count()
        active = Clinic.objects.filter(is_active=True).count()
        inactive = Clinic.objects.filter(is_active=False).count()

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
        }
