"""
ADMIN CONFIGURATION - Kiosk App Admin
Đăng ký các models để quản lý trong Django Admin
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Clinic, CustomUser, Doctors, Insurance, Patients, ServiceExam


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin với các fields bổ sung
    Kế thừa từ UserAdmin để giữ các chức năng mặc định
    """

    # ============= LIST VIEW =============
    list_display = [
        "username",
        "email",
        "get_full_name_display",
        "role",
        "department",
        "employee_id",
        "is_active",
        "is_staff",
        "date_joined",
    ]

    list_filter = [
        "role",
        "department",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "gender",
    ]

    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
        "employee_id",
        "department",
    ]

    list_per_page = 25

    # ============= DETAIL VIEW =============
    # Thêm các fieldsets mới vào UserAdmin mặc định
    fieldsets = (UserAdmin.fieldsets or ()) + (  # type: ignore
        ("📞 Thông tin liên hệ", {"fields": ("phone", "address")}),
        ("💼 Thông tin công việc", {"fields": ("role", "department", "employee_id")}),
        ("👤 Thông tin cá nhân", {"fields": ("avatar", "date_of_birth", "gender")}),
        (
            "📝 Metadata",
            {
                "fields": ("created_by", "updated_at", "notes"),
                "classes": ("collapse",),  # Ẩn section này mặc định
            },
        ),
    )

    # Fieldsets cho trang thêm user mới
    add_fieldsets = (UserAdmin.add_fieldsets or ()) + (  # type: ignore
        ("📧 Thông tin cơ bản", {"fields": ("email", "first_name", "last_name")}),
        ("📞 Thông tin liên hệ", {"fields": ("phone", "address")}),
        ("💼 Thông tin công việc", {"fields": ("role", "department", "employee_id")}),
    )

    # Fields chỉ đọc
    readonly_fields = ["updated_at", "date_joined", "last_login"]

    # ============= CUSTOM METHODS =============

    @admin.display(description="Họ tên", ordering="first_name")
    def get_full_name_display(self, obj):
        """Hiển thị họ tên với icon theo role"""
        icons = {
            "admin": "👑",
            "doctor": "👨‍⚕️",
            "nurse": "👩‍⚕️",
            "receptionist": "💁",
            "accountant": "💼",
            "pharmacist": "💊",
            "technician": "🔧",
        }
        icon = icons.get(obj.role, "👤")
        return format_html("{} <strong>{}</strong>", icon, obj.full_name)

    # ============= ACTIONS =============

    actions = ["activate_users", "deactivate_users"]

    @admin.action(description="✅ Kích hoạt users đã chọn")
    def activate_users(self, request, queryset):
        """Kích hoạt nhiều users cùng lúc"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Đã kích hoạt {updated} người dùng.")

    @admin.action(description="❌ Vô hiệu hóa users đã chọn")
    def deactivate_users(self, request, queryset):
        """Vô hiệu hóa nhiều users cùng lúc"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Đã vô hiệu hóa {updated} người dùng.")


# ============= ĐĂNG KÝ CÁC MODELS KHÁC =============
# TODO: Tạo custom admin cho các models khác

# @admin.register(Patients)
# class PatientsAdmin(admin.ModelAdmin):
#     list_display = ['full_name', 'phone', 'created_at']
#     search_fields = ['full_name', 'phone']

# @admin.register(Doctors)
# class DoctorsAdmin(admin.ModelAdmin):
#     list_display = ['name', 'specialty', 'clinic']
#     search_fields = ['name', 'specialty']

# @admin.register(Clinic)
# class ClinicAdmin(admin.ModelAdmin):
#     list_display = ['name', 'address', 'is_active']
#     search_fields = ['name', 'address']
#     list_display = ['name', 'address', 'is_active']
#     search_fields = ['name', 'address']
#     search_fields = ['name', 'address']
