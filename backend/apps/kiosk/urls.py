"""
ROUTING CONFIGURATION - Kiosk App URLs
=====================================
Quản lý routing cho Healthcare Kiosk API endpoints

Cấu trúc URL (sau khi combine với config/urls.py):
- /api/users/          → Quản lý users (tài khoản hệ thống)
- /api/patients/       → Quản lý bệnh nhân
- /api/insurance/      → Quản lý bảo hiểm y tế
- /api/doctors/        → Quản lý bác sĩ
- /api/clinics/        → Quản lý phòng khám
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import ViewSets (Controllers trong Clean Architecture)
from apps.kiosk.views import (
    UserViewSet,
    PatientViewSet,
    InsuranceViewSet,
    DoctorViewSet,
    ClinicViewSet,
    ServiceExamViewSet
)
from kiosk.views.order_view import OrderViewSet

# Namespace cho app (dùng trong reverse URL: 'kiosk:user-list')
app_name = 'kiosk'

# ===== DRF ROUTER CONFIGURATION =====
# DefaultRouter tự động tạo URL patterns cho CRUD operations
# Documentation: https://www.django-rest-framework.org/api-guide/routers/
router = DefaultRouter()

# ===== ROUTER REGISTRATION =====
# Format: router.register(r'url-prefix', ViewSetClass, basename='url-name')
# 
#  LƯU Ý QUAN TRỌNG VỀ THỨ TỰ ĐĂNG KÝ:
# - Đăng ký các route CỤ THỂ (users, clinics...) trước
# - KHÔNG đăng ký route RỖNG (r'') ở giữa danh sách
# - Nếu có route rỗng, phải đặt CUỐI CÙNG
# - Thứ tự ảnh hưởng đến URL matching: Django kiểm tra từ trên xuống
# 
#   router.register(r'users', UserViewSet)      #  Route cụ thể trước
#   router.register(r'clinics', ClinicViewSet)  #  Route cụ thể
#   router.register(r'', SomeViewSet)           #  Route rỗng cuối cùng
router = DefaultRouter(trailing_slash=False) # tắt slash cuối URL /api/users thay vì /api/users/
router.register(r'/users', UserViewSet, basename='user')
router.register(r'/patients', PatientViewSet, basename='patient')
router.register(r'/insurance', InsuranceViewSet, basename='insurance')
router.register(r'/doctors', DoctorViewSet, basename='doctor')
router.register(r'/clinics', ClinicViewSet, basename='clinic')
router.register(r'/service-exams', ServiceExamViewSet, basename='service-exam')
router.register(r'/orders', OrderViewSet, basename='order')
# ===== URL PATTERNS =====
urlpatterns = [
    # Include tất cả routes từ router
    # Kết hợp với config/urls.py → /api/users, /api/doctors...
    path('', include(router.urls)),
]