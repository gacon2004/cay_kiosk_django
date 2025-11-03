"""
Test view đơn giản để kiểm tra API có hoạt động không
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def test_api(request):
    """
    API test đơn giản - không cần authentication
    """
    return Response({
        'message': 'API is working!',
        'status': 'success'
    })
