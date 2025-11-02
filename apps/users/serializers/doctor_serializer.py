"""
VIEW LAYER (Serializers) - Doctor Serializer
Chuyển đổi Doctor model thành JSON và validate input
"""
from rest_framework import serializers
from apps.users.models import Doctors


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer cho bác sĩ"""
    
    title = serializers.ReadOnlyField(help_text="Danh xưng bác sĩ")
    user_username = serializers.CharField(source='user_id.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Doctors
        fields = [
            'id',
            'doctor_id',
            'full_name',
            'title',
            'specialization',
            'phone',
            'email',
            'user_id',
            'user_username',
            'years_of_experience',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_doctor_id(self, value):
        """Validate mã bác sĩ"""
        if not value.startswith('BS'):
            raise serializers.ValidationError("Mã bác sĩ phải bắt đầu bằng 'BS'")
        return value.upper()
    
    def validate_years_of_experience(self, value):
        """Validate số năm kinh nghiệm"""
        if value < 0:
            raise serializers.ValidationError("Số năm kinh nghiệm không được âm")
        if value > 60:
            raise serializers.ValidationError("Số năm kinh nghiệm không hợp lệ")
        return value


class DoctorListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách bác sĩ"""
    
    title = serializers.ReadOnlyField()
    
    class Meta:
        model = Doctors
        fields = ['id', 'doctor_id', 'full_name', 'title', 'specialization', 'phone', 'is_active']


class DoctorDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho bác sĩ"""
    
    title = serializers.ReadOnlyField()
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctors
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_user_info(self, obj):
        """Lấy thông tin user liên kết"""
        if obj.user_id:
            return {
                'id': obj.user_id.id,
                'username': obj.user_id.username,
                'email': obj.user_id.email,
                'is_active': obj.user_id.is_active,
            }
        return None
