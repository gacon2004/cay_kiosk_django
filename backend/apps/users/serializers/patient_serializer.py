"""
VIEW LAYER (Serializers) - Patient Serializer
Chuyển đổi Patient model thành JSON và validate input
"""
from rest_framework import serializers
from apps.users.models import Patients


class PatientSerializer(serializers.ModelSerializer):
    """Serializer cho bệnh nhân"""
    
    age = serializers.ReadOnlyField(help_text="Tuổi tính tự động")
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Patients
        fields = [
            'id',
            'national_id',
            'full_name',
            'date_of_birth',
            'age',
            'gender',
            'phone',
            'ward',
            'district',
            'city',
            'full_address',
            'occupation',
            'ethnicity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'age')
    
    def get_full_address(self, obj):
        """Lấy địa chỉ đầy đủ"""
        return obj.get_full_address()
    
    def validate_national_id(self, value):
        """Validate số CMND/CCCD"""
        if not value.isdigit():
            raise serializers.ValidationError("CMND/CCCD phải là số")
        if len(value) not in [9, 12]:
            raise serializers.ValidationError("CMND phải 9 số hoặc CCCD phải 12 số")
        return value
    
    def validate_date_of_birth(self, value):
        """Validate ngày sinh"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Ngày sinh không thể lớn hơn ngày hiện tại")
        
        age = date.today().year - value.year
        if age > 150:
            raise serializers.ValidationError("Tuổi không hợp lệ")
        
        return value


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách bệnh nhân"""
    
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Patients
        fields = ['id', 'national_id', 'full_name', 'date_of_birth', 'age', 'gender', 'phone']
        read_only_fields = ('id',)


class PatientDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho bệnh nhân (bao gồm insurance)"""
    
    age = serializers.ReadOnlyField()
    full_address = serializers.SerializerMethodField()
    insurances = serializers.SerializerMethodField()
    
    class Meta:
        model = Patients
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_full_address(self, obj):
        return obj.get_full_address()
    
    def get_insurances(self, obj):
        """Lấy danh sách bảo hiểm của bệnh nhân"""
        from .insurance_serializer import InsuranceSerializer
        insurances = obj.insurances.all()
        return InsuranceSerializer(insurances, many=True).data
