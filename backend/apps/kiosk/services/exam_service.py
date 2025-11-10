from typing import Dict, List, Optional

from apps.kiosk.models import ServiceExam
from django.db import models


class ExamService:
    """
    Service class xử lý business logic cho dịch vụ khám bệnh
    """

    @staticmethod
    def get_all_exams() -> models.QuerySet[ServiceExam]:
        """Lấy tất cả dịch vụ khám bệnh"""
        return ServiceExam.objects.all()

    @staticmethod
    def get_exam_by_id(exam_id: int) -> Optional[ServiceExam]:
        """Lấy dịch vụ khám bệnh theo ID"""
        try:
            return ServiceExam.objects.get(id=exam_id)
        except ServiceExam.DoesNotExist:
            return None

    @staticmethod
    def get_exam_by_name(name_service: str) -> Optional[ServiceExam]:
        """Lấy dịch vụ khám bệnh theo tên"""
        return ServiceExam.objects.filter(name=name_service).first()

    @staticmethod
    def create_service_exam(
        name: str, description: str, price_non_insurance: float, price_insurance: float
    ) -> ServiceExam:
        """
        Tạo dịch vụ khám bệnh mới với validation

        Args:
            name (str): Tên dịch vụ
            description (str): Mô tả dịch vụ
            price_non_insurance (float): Giá dịch vụ không bảo hiểm
            price_insurance (float): Giá dịch vụ có bảo hiểm

        Returns:
            ServiceExam: Dịch vụ khám bệnh mới tạo

        Raises:
            ValueError: Nếu validation thất bại
        """
        # Validation
        if ServiceExam.objects.filter(name=name).exists():
            raise ValueError(f"Dịch vụ khám '{name}' đã tồn tại")

        if price_non_insurance <= 0 or price_insurance <= 0:
            raise ValueError("Giá dịch vụ phải lớn hơn 0")

        if price_insurance > price_non_insurance:
            raise ValueError("Giá bảo hiểm không được cao hơn giá thường")

        exam_service = ServiceExam.objects.create(
            name=name,
            description=description,
            prices_non_insurance=price_non_insurance,
            prices_insurance=price_insurance,
        )
        return exam_service

    @staticmethod
    def update_service_exam(exam: ServiceExam, data: Dict) -> ServiceExam:
        """Cập nhật dịch vụ khám bệnh"""
        for key, value in data.items():
            setattr(exam, key, value)
        exam.save()
        return exam

    @staticmethod
    def delete_service_exam(exam: ServiceExam) -> None:
        """Xóa dịch vụ khám bệnh"""
        exam.delete()

    @staticmethod
    def search_exams(search_term: str) -> models.QuerySet[ServiceExam]:
        """Tìm kiếm dịch vụ khám bệnh theo từ khóa"""
        return ServiceExam.objects.filter(
            models.Q(name__icontains=search_term)
            | models.Q(description__icontains=search_term)
        )

    @staticmethod
    def get_exams_by_price_range(
        min_price: float, max_price: float
    ) -> models.QuerySet[ServiceExam]:
        """Lấy dịch vụ khám trong khoảng giá"""
        return ServiceExam.objects.filter(
            prices_non_insurance__gte=min_price, prices_non_insurance__lte=max_price
        )

    @staticmethod
    def get_exams_ordered_by_price(desc: bool = False) -> models.QuerySet[ServiceExam]:
        """Lấy dịch vụ khám sắp xếp theo giá"""
        ordering = "-prices_non_insurance" if desc else "prices_non_insurance"
        return ServiceExam.objects.order_by(ordering)
