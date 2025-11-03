# Django REST Framework - Decorators & Annotations Guide

## 📋 Tổng quan

File này giải thích các decorator/annotation thường dùng trong Django REST Framework ViewSet.

---

## 🎯 Class-based Decorators

### 1. `@method_decorator(decorator, name='method_name')`

**Công dụng**: Apply decorator lên method của class

```python
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class MyViewSet(viewsets.ModelViewSet):
    pass
```

**Khi nào dùng:**
- ❌ **KHÔNG NÊN** dùng `@csrf_exempt` trong production
- ✅ Chỉ dùng khi cần apply Django decorator lên class-based view

**Lý do KHÔNG dùng @csrf_exempt:**
- Tắt bảo vệ CSRF → dễ bị tấn công
- REST API có cơ chế bảo vệ khác (Token-based)
- DRF tự động xử lý CSRF nếu config đúng

**Thay thế:** Dùng Token Authentication hoặc Session Authentication

---

## 🔐 Permission Classes

### 2. `permission_classes = [PermissionClass]`

**Công dụng**: Kiểm soát ai được phép truy cập API

```python
from rest_framework.permissions import (
    AllowAny,           # Cho phép tất cả (public API)
    IsAuthenticated,    # Phải đăng nhập
    IsAdminUser,        # Phải là admin
)

class ClinicViewSet(viewsets.ModelViewSet):
    # ⚠️ CHỈ DÙNG TRONG DEVELOPMENT
    permission_classes = [AllowAny]
    
    # ✅ PRODUCTION nên dùng:
    # permission_classes = [IsAuthenticated]
```

**Best practice:**
```python
def get_permissions(self):
    """Phân quyền theo từng action"""
    if self.action in ['create', 'update', 'destroy']:
        return [IsAdminUser()]  # Admin mới được sửa/xóa
    return [IsAuthenticated()]  # Các action khác cần login
```

**Permission classes phổ biến:**
- `AllowAny`: Cho phép tất cả (development/public API)
- `IsAuthenticated`: Phải đăng nhập
- `IsAdminUser`: Phải là admin
- `IsAuthenticatedOrReadOnly`: Đọc free, ghi cần login
- Custom permission: Tự định nghĩa

---

## 🎬 Action Decorator

### 3. `@action(detail=True/False, methods=[...])`

**Công dụng**: Tạo custom endpoint ngoài CRUD mặc định

```python
from rest_framework.decorators import action

class ClinicViewSet(viewsets.ModelViewSet):
    # CRUD mặc định: list, create, retrieve, update, destroy
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        GET /clinics/active/
        
        detail=False → URL không cần {id}
        methods=['get'] → Chỉ cho phép GET
        """
        pass
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        POST /clinics/{id}/activate/
        
        detail=True → URL cần {id}
        methods=['post'] → Chỉ cho phép POST
        pk → Primary key lấy từ URL
        """
        pass
```

**Parameters:**
- `detail=False`: URL không cần `{id}` → `/resource/action/`
- `detail=True`: URL cần `{id}` → `/resource/{id}/action/`
- `methods`: HTTP methods cho phép (get, post, put, patch, delete)
- `url_path`: Custom URL path (default: tên method)
- `url_name`: Custom URL name (default: tên method)
- `permission_classes`: Override permission cho action này

**Ví dụ nâng cao:**
```python
@action(
    detail=True,
    methods=['post'],
    permission_classes=[IsAdminUser],
    url_path='send-notification',  # URL: /clinics/{id}/send-notification/
    url_name='send-notification'
)
def send_notification(self, request, pk=None):
    """Custom URL path và permission"""
    pass
```

---

## 📦 ModelViewSet

### 4. `class MyViewSet(viewsets.ModelViewSet)`

**Công dụng**: ViewSet có sẵn CRUD operations

**Tự động có các actions:**
```python
class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    
    # TỰ ĐỘNG CÓ:
    # list()    → GET    /clinics/           → Danh sách
    # create()  → POST   /clinics/           → Tạo mới
    # retrieve()→ GET    /clinics/{id}/      → Chi tiết
    # update()  → PUT    /clinics/{id}/      → Update toàn bộ
    # partial_update() → PATCH /clinics/{id}/ → Update 1 phần
    # destroy() → DELETE /clinics/{id}/      → Xóa
```

**Các ViewSet khác:**
- `ModelViewSet`: Đầy đủ CRUD (dùng nhiều nhất)
- `ReadOnlyModelViewSet`: Chỉ list + retrieve (read-only)
- `GenericViewSet`: Base class (tự implement actions)

---

## 🔄 Override Methods

### 5. `get_serializer_class()`

**Công dụng**: Dùng serializer khác nhau cho từng action

```python
def get_serializer_class(self):
    if self.action == 'list':
        return ClinicListSerializer  # Rút gọn cho list
    elif self.action == 'create':
        return ClinicCreateSerializer  # Validate khi tạo
    return ClinicSerializer  # Default
```

### 6. `get_queryset()`

**Công dụng**: Filter queryset theo context

```python
def get_queryset(self):
    user = self.request.user
    if user.is_staff:
        return Clinic.objects.all()  # Admin thấy tất cả
    return Clinic.objects.filter(owner=user)  # User chỉ thấy của mình
```

---

## 🛡️ Best Practices

### ✅ ĐÚNG (Production-ready):

```python
class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsAuthenticated]  # Phải login
    
    def get_permissions(self):
        """Phân quyền chi tiết"""
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def list(self, request):
        """GỌI Service layer"""
        clinics = ClinicService.get_all_clinics()
        serializer = self.get_serializer(clinics, many=True)
        return Response(serializer.data)
```

### ❌ SAI (Không nên):

```python
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')  # ❌ Tắt CSRF
class ClinicViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # ❌ Cho phép tất cả
    
    def list(self, request):
        """❌ Business logic trong View"""
        queryset = Clinic.objects.filter(...)  # ❌ Query trực tiếp
        return Response(...)
```

---

## 📚 Tài liệu tham khảo

- **ViewSets**: https://www.django-rest-framework.org/api-guide/viewsets/
- **Actions**: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
- **Permissions**: https://www.django-rest-framework.org/api-guide/permissions/
- **Serializers**: https://www.django-rest-framework.org/api-guide/serializers/

---

## 🎓 Tóm tắt

| Decorator/Annotation | Dùng khi nào | Nên/Không nên |
|---------------------|-------------|---------------|
| `@method_decorator` | Apply Django decorator | ⚠️ Hạn chế dùng |
| `@csrf_exempt` | Tắt CSRF | ❌ KHÔNG dùng production |
| `permission_classes` | Phân quyền | ✅ BẮT BUỘC có |
| `@action` | Custom endpoint | ✅ Dùng thường xuyên |
| `ModelViewSet` | CRUD API | ✅ Best choice |

---

**Lưu ý quan trọng:**
- ⚠️ **KHÔNG BAO GIỜ** dùng `@csrf_exempt` trong production
- ✅ **LUÔN LUÔN** set `permission_classes`
- ✅ **LUÔN LUÔN** gọi Service layer thay vì query trực tiếp
- ✅ **LUÔN LUÔN** validate input với Serializer
