from apps.kiosk.models import Doctors
from pydantic import ValidationError


class DoctorService:
    @staticmethod
    def get_doctor_by_id(doctor_id: int) -> Doctors:
        """
        Args:
            doctor_id (int): ID bác sĩ
        Returns:
            Doctor: Instance bác sĩ
        Raises:
            ValidationError: Nếu không tìm thấy bác sĩ
        """
        try:
            return Doctors.objects.get(id=doctor_id)
        except Doctors.DoesNotExist:
            raise ValidationError(f"Không tìm thấy bác sĩ với ID {doctor_id}")

    @staticmethod
    def get_list_doctor():
        """
        Lấy danh sách tất cả bác sĩ
        """
        return Doctors.objects.all().order_by("full_name")

    @staticmethod
    def add_doctor(doctor_data: dict):
        """
        Tạo mới một bác sĩ

        Args:
            doctor_data (dict): Dữ liệu bác sĩ
        Returns:
            Doctor: Instance bác sĩ mới tạo
        """
        doctor = Doctors.objects.create(**doctor_data)
        return doctor

    @staticmethod
    def update_doctor(doctor_id: int, update_data: dict):
        """
        Cập nhật thông tin bác sĩ

        Args:
            doctor_id (int): ID bác sĩ cần cập nhật
            update_data (dict): Dữ liệu cập nhật
        Returns:
            Doctor: Instance bác sĩ đã được cập nhật
        Raises:
            ValidationError: Nếu không tìm thấy bác sĩ
        """
        doctor = DoctorService.get_doctor_by_id(doctor_id)
        for key, value in update_data.items():
            setattr(doctor, key, value)
        doctor.save()
        return doctor
