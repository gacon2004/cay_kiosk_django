"""
VIEW LAYER (Serializers) - User Serializer
Serializers cho Django User model
"""

# Import serializers từ Django REST Framework để chuyển đổi dữ liệu
from rest_framework import serializers
# Import hàm get_user_model để lấy model User đang sử dụng trong project
from django.contrib.auth import get_user_model

# Lấy model User (có thể là User mặc định hoặc custom User)
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer cơ bản cho User
    Dùng để serialize/deserialize dữ liệu User đầy đủ
    """

    # Tạo field tùy chỉnh full_name, sẽ được tính toán bởi method get_full_name
    full_name = serializers.SerializerMethodField()

    class Meta:
        # Chỉ định model để serialize
        model = User
        # Danh sách các fields sẽ được trả về trong JSON
        fields = [
            "id",            # ID user
            "username",      # Tên đăng nhập
            "email",         # Email
            "first_name",    # Tên
            "last_name",     # Họ
            "full_name",     # Họ tên đầy đủ (custom field)
            "is_active",     # Trạng thái active
            "is_staff",      # Có phải staff không
            "date_joined",   # Ngày tạo tài khoản
            "last_login",    # Lần login cuối
        ]
        # Các fields chỉ đọc, không cho phép client cập nhật
        read_only_fields = ["id", "date_joined", "last_login"]

    def get_full_name(self, obj):
        """
        Method để tính toán full_name
        obj: instance của User model
        Ghép first_name + last_name, nếu trống thì trả về username
        """
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer đơn giản cho danh sách users
    Chỉ trả về các fields cần thiết để hiển thị trong list
    Giúp giảm dung lượng response khi query nhiều users
    """

    # Field tùy chỉnh full_name
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Chỉ lấy các fields quan trọng để hiển thị list
        fields = ["id", "username", "email", "full_name", "is_active", "is_staff"]

    def get_full_name(self, obj):
        """Ghép họ tên từ first_name và last_name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer cho tạo user mới
    Xử lý validation password và hash password trước khi lưu
    """

    # Field password, write_only=True nghĩa là chỉ nhận input, không trả về trong response
    password = serializers.CharField(write_only=True, min_length=8)
    # Field xác nhận password (phải giống password)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        # Các fields cần thiết khi tạo user mới
        fields = [
            "username",      # Tên đăng nhập (bắt buộc)
            "email",         # Email
            "password",      # Mật khẩu
            "password2",     # Xác nhận mật khẩu
            "first_name",    # Tên
            "last_name",     # Họ
        ]

    def validate(self, data):
        """
        Validate toàn bộ data trước khi create
        Kiểm tra password và password2 có khớp nhau không
        """
        # So sánh password và password2
        if data.get("password") != data.get("password2"):
            # Nếu không khớp, raise ValidationError
            raise serializers.ValidationError({"password2": "Mật khẩu không khớp"})
        # Nếu khớp, return data để tiếp tục xử lý
        return data

    def create(self, validated_data):
        """
        Override method create để xử lý password
        validated_data: dữ liệu đã qua validation
        """
        # Xóa password2 vì không cần lưu vào database
        validated_data.pop("password2")
        # Lấy password ra khỏi validated_data
        password = validated_data.pop("password")

        # Tạo user với các fields còn lại (username, email, first_name, last_name)
        user = User.objects.create(**validated_data)
        # Hash password và lưu (KHÔNG lưu plain text password)
        user.set_password(password)
        user.save()

        # Trả về user đã tạo
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer cho cập nhật user
    Chỉ cho phép update các fields an toàn (không cho update username, password)
    """

    class Meta:
        model = User
        # Chỉ cho phép update các fields này
        fields = ["email", "first_name", "last_name", "is_active"]

    def validate_email(self, value):
        """
        Validate email không bị trùng với user khác
        value: giá trị email mới
        """
        # Lấy instance đang được update (user hiện tại)
        user = self.instance
        # Kiểm tra có user nào khác (exclude user hiện tại) đã dùng email này chưa
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            # Nếu có user khác dùng email này rồi, raise error
            raise serializers.ValidationError("Email đã được sử dụng")
        # Nếu email hợp lệ, return value
        return value
