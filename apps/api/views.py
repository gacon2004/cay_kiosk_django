from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
# API views sẽ được tạo ở đây nếu cần
# Hiện tại user API đã được tạo trong apps.users

@api_view(['GET'])
def api_root(request):
    """
    API Root - Danh sách các endpoints có sẵn
    """
    return Response({
        'message': 'Welcome to Healthcare Kiosk API',
        'endpoints': {
            'authentication': '/api/auth/',
            'users': '/api/users/',
        }
    })