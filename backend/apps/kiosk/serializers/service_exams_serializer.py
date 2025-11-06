# Import serializers từ Django REST Framework để chuyển đổi dữ liệu
from typing import Any

from apps.kiosk.models import ServiceExam
from rest_framework import serializers


class ServiceExamsCreateSerializer(serializers.Serializer):
    """
    Serializer cho việc tạo mới dịch vụ exams
    Xác thực và chuyển đổi dữ liệu đầu vào từ client
    """

    service_name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    price_insurance = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_non_insurance = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data: dict[str, Any]) -> ServiceExam:
        """
        Tạo instance ServiceExam mới từ dữ liệu đã được xác thực
        Args:
            validated_data: Dữ liệu đã được xác thực từ client
        Returns:
            ServiceExam: Instance dịch vụ exams vừa tạo
        """
        return ServiceExam.objects.create(
            name=validated_data["service_name"],
            description=validated_data.get("description", ""),
            prices_insurance=validated_data["price_insurance"],
            prices_non_insurance=validated_data["price_non_insurance"],
        )


class ServiceExamsListSerializer(serializers.ModelSerializer):
    """
    Serializer rút gọn cho danh sách dịch vụ exams
    Chỉ trả về các fields cần thiết cho list view
    Giúp giảm dung lượng response
    """

    class Meta:
        model = ServiceExam
        # Chỉ lấy các fields quan trọng
        fields = ["name", "description", "prices_insurance", "prices_non_insurance"]


class ServiceExamsDetailSerializer(serializers.ModelSerializer):
    """
    Serializer chi tiết cho dịch vụ exams
    Trả về tất cả các fields của model ServiceExam
    Dùng cho detail view khi cần thông tin đầy đủ
    """

    class Meta:
        model = ServiceExam
        # Lấy tất cả các fields của model
        fields = "__all__"


class ServiceExamsUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc cập nhật dịch vụ exams
    Chỉ cho phép cập nhật các fields nhất định
    """

    class Meta:
        model = ServiceExam
        # Chỉ cho phép cập nhật các fields này
        fields = [
            "description",
            "prices_insurance",
            "prices_non_insurance",
        ]  # Chỉ cho phép cập nhật các fields này
        fields = ["description", "prices_insurance", "prices_non_insurance"]
