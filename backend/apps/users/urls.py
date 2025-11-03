"""
ROUTING - Users App URLs
Map URLs tới các ViewSets (Controllers)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import các ViewSets từ thư mục views (MVC structure)
from apps.users.views import (
    UserViewSet,
    PatientViewSet,
    InsuranceViewSet,
    DoctorViewSet,
    ClinicViewSet,  # Import ClinicViewSet
)
from apps.users.views.test_view import test_api  # Import test view

app_name = 'users'

# Router cho API ViewSet
# Router tự động tạo URL patterns cho các actions CRUD
router = DefaultRouter()
# Nguyên nhân chính: Thứ tự đăng ký router trong urls.py bị sai. 
# Khi bạn đăng ký UserViewSet với route rỗng (r'') trước các route khác,
# Django Router sẽ cố gắng match /api/users/clinics/ như một phần của UserViewSet 
# (có thể là action hoặc object lookup), và UserViewSet có get_permissions() 
# yêu cầu IsAuthenticated() → gây ra lỗi 403.

# Đăng ký các ViewSets - ĐẶT CÁC ROUTE CỤ THỂ TRƯỚC ROUTE RỖNG!
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'insurance', InsuranceViewSet, basename='insurance')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'clinics', ClinicViewSet, basename='clinic')  # Đăng ký route cho Clinic
router.register(r'', UserViewSet, basename='user')  # Route rỗng đặt cuối cùng

urlpatterns = [
    path('test/', test_api, name='test-api'),  # Test API endpoint
    path('', include(router.urls)),
]

"""
Generated URL Patterns:
========================

Users:
- GET    /api/users/                      - List users
- POST   /api/users/                      - Create user
- GET    /api/users/{id}/                 - Retrieve user
- PUT    /api/users/{id}/                 - Update user
- PATCH  /api/users/{id}/                 - Partial update
- DELETE /api/users/{id}/                 - Delete user
- GET    /api/users/me/                   - Current user
- GET    /api/users/active/               - Active users
- POST   /api/users/{id}/activate/        - Activate user
- POST   /api/users/{id}/deactivate/      - Deactivate user

Patients:
- GET    /api/users/patients/             - List patients
- POST   /api/users/patients/             - Create patient
- GET    /api/users/patients/{id}/        - Retrieve patient
- PUT    /api/users/patients/{id}/        - Update patient
- PATCH  /api/users/patients/{id}/        - Partial update
- DELETE /api/users/patients/{id}/        - Delete patient
- GET    /api/users/patients/with_insurance/           - Patients with insurance
- GET    /api/users/patients/search_by_national_id/    - Search by national ID
- GET    /api/users/patients/{id}/insurances/          - Patient's insurances

Insurance:
- GET    /api/users/insurance/            - List insurances
- POST   /api/users/insurance/            - Create insurance
- GET    /api/users/insurance/{id}/       - Retrieve insurance
- PUT    /api/users/insurance/{id}/       - Update insurance
- PATCH  /api/users/insurance/{id}/       - Partial update
- DELETE /api/users/insurance/{id}/       - Delete insurance
- GET    /api/users/insurance/valid/      - Valid insurances
- GET    /api/users/insurance/expired/    - Expired insurances
- GET    /api/users/insurance/expiring_soon/  - Expiring soon
- GET    /api/users/insurance/{id}/check_validity/  - Check validity

Doctors:
- GET    /api/users/doctors/              - List doctors
- POST   /api/users/doctors/              - Create doctor
- GET    /api/users/doctors/{id}/         - Retrieve doctor
- PUT    /api/users/doctors/{id}/         - Update doctor
- PATCH  /api/users/doctors/{id}/         - Partial update
- DELETE /api/users/doctors/{id}/         - Delete doctor
- GET    /api/users/doctors/by_specialization/  - Search by specialization
- GET    /api/users/doctors/active/       - Active doctors
- GET    /api/users/doctors/specializations/    - List specializations
- POST   /api/users/doctors/{id}/activate/      - Activate doctor
- POST   /api/users/doctors/{id}/deactivate/    - Deactivate doctor

Clinics:
- GET    /api/users/clinics/              - List clinics

"""
