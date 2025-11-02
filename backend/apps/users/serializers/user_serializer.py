"""
VIEW LAYER (Serializers) - User Serializer
Serializers cho Django User model
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer cơ bản cho User"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'is_active',
            'is_staff',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        """Lấy họ tên đầy đủ"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class UserListSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho danh sách users"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'is_active', 'is_staff']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer cho tạo user mới"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
        ]
    
    def validate(self, data):
        """Validate passwords match"""
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError({
                'password2': "Mật khẩu không khớp"
            })
        return data
    
    def create(self, validated_data):
        """Tạo user với password đã hash"""
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer cho cập nhật user"""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'is_active']
    
    def validate_email(self, value):
        """Validate email không trùng"""
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Email đã được sử dụng")
        return value
