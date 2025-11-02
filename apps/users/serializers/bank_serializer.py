"""
VIEW LAYER (Serializers) - Bank Information Serializer
Chuyển đổi BankInformation model thành JSON và validate input
"""
from rest_framework import serializers
from apps.users.models import BankInformation


class BankInformationSerializer(serializers.ModelSerializer):
    """Serializer cho thông tin ngân hàng"""
    
    masked_account_number = serializers.SerializerMethodField(
        help_text="Số tài khoản đã che"
    )
    
    class Meta:
        model = BankInformation
        fields = [
            'id',
            'bank_id',
            'bank_name',
            'account_number',
            'masked_account_number',
            'account_holder',
            'branch',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'account_number': {'write_only': True}  # Không hiển thị số tài khoản đầy đủ
        }
    
    def get_masked_account_number(self, obj):
        """Trả về số tài khoản đã che"""
        return obj.get_masked_account_number()
    
    def validate_account_number(self, value):
        """Validate số tài khoản"""
        if not value.isdigit():
            raise serializers.ValidationError("Số tài khoản phải là số")
        if len(value) < 6:
            raise serializers.ValidationError("Số tài khoản không hợp lệ")
        return value
    
    def validate_bank_id(self, value):
        """Validate mã ngân hàng"""
        return value.upper()


class BankInformationListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách ngân hàng"""
    
    masked_account_number = serializers.SerializerMethodField()
    
    class Meta:
        model = BankInformation
        fields = ['id', 'bank_id', 'bank_name', 'masked_account_number', 'is_active']
    
    def get_masked_account_number(self, obj):
        return obj.get_masked_account_number()
