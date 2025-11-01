from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, InsuranceViewSet, DoctorViewSet

# urlpatterns = [
#     path('users/', get_user, name='get_user'),
#     path('users/create/', create_user, name='create_user'),
#     path('users/<int:pk>/', user_detail, name='user_detail'),
# ]
router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'Insurance', InsuranceViewSet)
router.register(r'Doctors', DoctorViewSet)

urlpatterns = router.urls
