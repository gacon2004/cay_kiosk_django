from typing import Optional
from apps.kiosk.models import ServiceExam

class ExamService:
    """
    Service class xử lý business logic cho dịch vụ khám bệnh
    """
    @staticmethod
    def get_exam_by_name(name_service: str) -> Optional[ServiceExam]:
        return ServiceExam.objects.filter(name=name_service).first()
    
    @staticmethod
    def create_service_exam(name: str, description: str, price_non_insurance: float, price_insurance: float) -> ServiceExam:
        """
        Tạo dịch vụ khám bệnh mới
        Args:
            name (str): Tên dịch vụ
            description (str): Mô tả dịch vụ
            price_non_insurance (float): Giá dịch vụ không bảo hiểm
            price_insurance (float): Giá dịch vụ có bảo hiểm
        Returns:
            ServiceExam: Dịch vụ khám bệnh mới tạo
        """
        exam_service = ServiceExam.objects.create(
            name=name,
            description=description,
            prices_non_insurance=price_non_insurance,
            prices_insurance=price_insurance
        )
        return exam_service