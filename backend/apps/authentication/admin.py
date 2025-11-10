from typing import Any

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

# cấu hình giao diện quản trị Django Admin cho các models. Đây là một phần quan trọng của Django framework giúp tạo ra giao diện web để quản lý dữ liệu mà không cần code HTML/CSS phức tạp

# Lấy model User hiện tại (CustomUser) từ settings.AUTH_USER_MODEL
User = get_user_model()


# Đăng ký model CustomUser với Django Admin
# Tạo giao diện CRUD (Create, Read, Update, Delete) tự động
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin cho model CustomUser (user model tùy chỉnh).

    Cung cấp list display, filters, search và một số actions tiện lợi.
    Kế thừa từ UserAdmin để giữ các chức năng mặc định của Django admin.
    """

    # Danh sách các trường hiển thị trong trang list view của admin
    list_display = [
        "username",
        "email",
        "get_full_name_display",  # Họ tên với icon (method tùy chỉnh)
        "role",
        "employee_id",
        "is_active",
        "is_staff",
        "date_joined",
    ]

    # Các filter để lọc danh sách users
    list_filter = [
        "role",
        "department",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "gender",
    ]

    # Các trường có thể search
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
        "employee_id",
        "department",
    ]

    # Số items hiển thị mỗi trang
    list_per_page = 25

    # Thêm các fieldsets tùy chỉnh để hiển thị fields bổ sung
    # Sử dụng list(...) để thỏa mãn type checker
    fieldsets = list(getattr(UserAdmin, "fieldsets", ())) + [  # type: ignore
        (
            "Thông tin liên hệ",
            {"fields": ("phone", "address")},
        ),  # Section cho thông tin liên hệ
        (
            "Thông tin công việc",
            {"fields": ("role", "department", "employee_id")},
        ),  # Section cho công việc
        (
            "Thông tin cá nhân",
            {"fields": ("avatar", "dob", "gender")},
        ),  # Section cho cá nhân
        (
            "Metadata",  # Section cho metadata
            {
                "fields": ("created_by", "updated_at", "notes"),  # Các trường metadata
                "classes": ("collapse",),  # Ẩn section này mặc định
            },
        ),
    ]

    # Fieldsets cho trang thêm user mới
    add_fieldsets = list(getattr(UserAdmin, "add_fieldsets", ())) + [  # type: ignore
        (
            "Thong tin co ban",
            {"fields": ("email", "first_name", "last_name")},
        ),  # Email và tên
        (
            "Thong tin lien he",
            {"fields": ("phone", "address")},
        ),  # Điện thoại và địa chỉ
        (
            "Thong tin cong viec",
            {"fields": ("role", "department", "employee_id")},
        ),  # Vai trò và công việc
    ]

    # Các trường chỉ đọc (không thể chỉnh sửa)
    readonly_fields = ["updated_at", "date_joined", "last_login"]

    # Method tùy chỉnh để hiển thị họ tên
    @admin.display(description="Ho ten", ordering="first_name")
    def get_full_name_display(self, obj: Any) -> str:
        # Trả về họ tên in đậm
        return format_html("<strong>{}</strong>", obj.full_name)

    # Các actions có thể thực hiện trên nhiều users cùng lúc
    actions = ["activate_users", "deactivate_users", "create_user"]

    # Action để kích hoạt nhiều users
    @admin.action(description="Kích hoạt users đã chọn")
    def activate_users(self, request, queryset):
        # Cập nhật is_active = True cho tất cả users trong queryset
        updated = queryset.update(is_active=True)
        # Hiển thị message cho user
        self.message_user(request, f"Đã kích hoạt {updated} người dùng.")

    # Action để vô hiệu hóa nhiều users
    @admin.action(description="Vô hiệu hóa users đã chọn")
    def deactivate_users(self, request, queryset):
        # Cập nhật is_active = False cho tất cả users trong queryset
        updated = queryset.update(is_active=False)
        # Hiển thị message cho user
        self.message_user(request, f"Đã vô hiệu hóa {updated} người dùng.")

    # Action để tạo user mới (chỉ dành cho admin)
    @admin.action(description="Tạo user mới (chỉ admin)")
    def create_user(self, request, queryset):
        """
        Action để tạo user mới từ admin.
        Chỉ admin mới có thể thực hiện action này.
        """
        # Kiểm tra user hiện tại có phải admin không
        if not request.user.is_superuser:  # type: ignore
            self.message_user(
                request, "Chỉ admin mới có thể tạo user mới.", level="ERROR"
            )
            return

        # Tạo user mới với thông tin mặc định
        try:
            # Tạo username tự động (có thể customize)
            base_username = "user_"
            counter = 1
            username = f"{base_username}{counter}"
            while User.objects.filter(username=username).exists():
                counter += 1
                username = f"{base_username}{counter}"

            # Tạo user mới
            user = User.objects.create(
                username=username,
                email=f"{username}@example.com",  # Email tạm thời
                first_name="",
                last_name="",
                is_active=True,
            )
            user.set_password("TempPass123!")  # type: ignore  # Mật khẩu tạm thời
            user.save()  # type: ignore

            # Thông báo thành công
            self.message_user(
                request,
                f"Đã tạo user mới: {username} (Mật khẩu tạm thời: TempPass123!)",
            )

        except Exception as e:
            self.message_user(request, f"Lỗi khi tạo user: {str(e)}", level="ERROR")
