"""
VIEW LAYER (Serializers) - Patient Serializer
Chuyển đổi Patient model thành JSON và validate input
"""

from rest_framework import serializers
from apps.users.models import Patients
from insurance_serializer import InsuranceSerializer

class PatientSerializer(serializers.ModelSerializer):
    """Serializer cho bệnh nhân"""

    age = serializers.ReadOnlyField(help_text="Tuổi tính tự động")
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = Patients
        fields = [
            "id",
            "national_id",
            "full_name",
            "date_of_birth",
            "age",
            "gender",
            "phone",
            "address",
            "occupation",
            "ethnicity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "age")

    def validate_national_id(self, national_id: str) -> str:
        """Validate số CMND/CCCD"""
        if not national_id.isdigit():
            raise serializers.ValidationError("CMND/CCCD phải là số")
        if len(national_id) not in [9, 12]:
            raise serializers.ValidationError("CMND phải 9 số hoặc CCCD phải 12 số")
        return national_id

    def validate_date_of_birth(self, date_of_birth: str) -> str:
        """Validate ngày sinh"""
        from datetime import date

        if date_of_birth > date.today():
            raise serializers.ValidationError(
                "Ngày sinh không thể lớn hơn ngày hiện tại"
            )

        age = date.today().year - date_of_birth.year
        if age > 150:
            raise serializers.ValidationError("Tuổi không hợp lệ")

        return date_of_birth


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách bệnh nhân"""
    age = serializers.ReadOnlyField()
    class Meta:
        model = Patients
        fields = [
            "id",
            "national_id",
            "full_name",
            "date_of_birth",
            "age",
            "gender",
            "phone",
        ]
        read_only_fields = ("id",)


class PatientDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho bệnh nhân (bao gồm insurance)"""

    age = serializers.ReadOnlyField()
    address = serializers.SerializerMethodField()
    insurances = serializers.SerializerMethodField()

    class Meta:
        model = Patients
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_insurances(self, obj: Patients) -> list[dict]:
        """Lấy danh sách bảo hiểm của bệnh nhân"""

        insurances = obj.insurances.all()
        return InsuranceSerializer(insurances, many=True).data
