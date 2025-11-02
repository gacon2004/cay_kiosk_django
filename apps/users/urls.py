from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Import các ViewSet cũ nếu có
try:
    from .views import PatientViewSet, InsuranceViewSet, DoctorViewSet
    HAS_OLD_MODELS = True
except:
    HAS_OLD_MODELS = False

app_name = 'users'

# Router cho API ViewSet
router = DefaultRouter()

# Đăng ký UserViewSet mới
router.register(r'', UserViewSet, basename='user')

# Đăng ký các ViewSet cũ nếu có
if HAS_OLD_MODELS:
    router.register(r'patients', PatientViewSet, basename='patient')
    router.register(r'insurance', InsuranceViewSet, basename='insurance')
    router.register(r'doctors', DoctorViewSet, basename='doctor')

urlpatterns = [
    path('', include(router.urls)),
]
