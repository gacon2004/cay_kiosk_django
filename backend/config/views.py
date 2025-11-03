"""
Home page view
"""
from django.http import JsonResponse


def home(request):
    """
    API Root - Hiển thị danh sách endpoints
    """
    return JsonResponse({
        'message': 'Welcome to Healthcare Kiosk API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api_root': '/api/',
            'authentication': '/api/auth/',
            'users': {
                'list': '/api/users/',
                'me': '/api/users/me/',
                'active': '/api/users/active/',
            },
            'patients': {
                'list': '/api/users/patients/',
                'with_insurance': '/api/users/patients/with_insurance/',
                'search_by_national_id': '/api/users/patients/search_by_national_id/?national_id=xxx',
            },
            'doctors': {
                'list': '/api/users/doctors/',
                'active': '/api/users/doctors/active/',
                'by_specialization': '/api/users/doctors/by_specialization/?specialization=xxx',
                'specializations': '/api/users/doctors/specializations/',
            },
            'insurance': {
                'list': '/api/users/insurance/',
                'valid': '/api/users/insurance/valid/',
                'expired': '/api/users/insurance/expired/',
                'expiring_soon': '/api/users/insurance/expiring_soon/',
            },
            'clinics': {
                'list': '/api/users/clinics/',
                'active': '/api/users/clinics/active/',
                'detail': '/api/users/clinics/{id}/',
                'activate': '/api/users/clinics/{id}/activate/',
                'deactivate': '/api/users/clinics/{id}/deactivate/',
            },
        },
        'documentation': {
            'swagger': '/api/swagger/',
            'redoc': '/api/redoc/',
        }
    })
