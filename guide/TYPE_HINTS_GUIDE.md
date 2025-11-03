# Python Type Hints Guide - Django Service Layer

## 📚 Giới thiệu

**Type Hints** (Python 3.5+) giúp:
- ✅ IDE tự động gợi ý code (autocomplete)
- ✅ Phát hiện lỗi sớm (type checking)
- ✅ Code dễ đọc, dễ hiểu hơn
- ✅ Documentation tự động

---

## 🎯 Cú pháp cơ bản

### 1. **Import types**

```python
from typing import Optional, Dict, Any, List, Tuple, Union
from django.db.models import QuerySet
from apps.users.models import Clinic
```

### 2. **Basic Types**

```python
def function_name(
    param1: str,              # String
    param2: int,              # Integer
    param3: bool,             # Boolean
    param4: float,            # Float
) -> str:                     # Return type là string
    return "result"
```

### 3. **Optional (có thể None)**

```python
from typing import Optional

def get_clinic(clinic_id: Optional[int] = None) -> Optional[Clinic]:
    """
    clinic_id: int hoặc None
    Returns: Clinic hoặc None
    """
    if clinic_id:
        return Clinic.objects.get(id=clinic_id)
    return None
```

### 4. **Dict (Dictionary)**

```python
from typing import Dict, Any

def create_clinic(data: Dict[str, Any]) -> Clinic:
    """
    data: Dictionary với key là string, value là bất kỳ kiểu gì
    Ví dụ: {"name": "Clinic A", "is_active": True}
    """
    return Clinic.objects.create(**data)

# Cụ thể hơn:
def update_clinic(data: Dict[str, str]) -> Clinic:
    """
    data: Dictionary với key và value đều là string
    """
    pass
```

### 5. **List (Danh sách)**

```python
from typing import List

def get_clinic_ids(clinics: List[Clinic]) -> List[int]:
    """
    clinics: Danh sách các Clinic objects
    Returns: Danh sách các int (IDs)
    """
    return [clinic.id for clinic in clinics]
```

### 6. **QuerySet (Django)**

```python
from django.db.models import QuerySet

def get_all_clinics() -> QuerySet[Clinic]:
    """
    Returns: Django QuerySet chứa Clinic objects
    """
    return Clinic.objects.all()
```

### 7. **Union (Nhiều kiểu)**

```python
from typing import Union

def find_clinic(identifier: Union[int, str]) -> Clinic:
    """
    identifier: Có thể là int (ID) hoặc str (name)
    """
    if isinstance(identifier, int):
        return Clinic.objects.get(id=identifier)
    return Clinic.objects.get(name=identifier)
```

### 8. **Tuple**

```python
from typing import Tuple

def get_clinic_info(clinic_id: int) -> Tuple[str, bool]:
    """
    Returns: (name, is_active)
    """
    clinic = Clinic.objects.get(id=clinic_id)
    return (clinic.name, clinic.is_active)
```

---

## 💡 Ví dụ thực tế - Service Layer

### **Ví dụ 1: CRUD Operations**

```python
from typing import Optional, Dict, Any
from django.db import transaction
from django.db.models import QuerySet
from apps.users.models import Clinic

class ClinicService:
    
    @staticmethod
    def get_all_clinics(
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> QuerySet[Clinic]:
        """
        Lấy danh sách clinics với filter
        
        Args:
            is_active: True/False/None - Filter theo trạng thái
            search: str hoặc None - Từ khóa tìm kiếm
        
        Returns:
            QuerySet[Clinic]: Django QuerySet
        """
        queryset = Clinic.objects.all()
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
    
    @staticmethod
    def get_clinic_by_id(clinic_id: int) -> Clinic:
        """
        Lấy 1 clinic
        
        Args:
            clinic_id: ID của clinic (int)
        
        Returns:
            Clinic: Instance của Clinic model
        """
        return Clinic.objects.get(id=clinic_id)
    
    @staticmethod
    @transaction.atomic
    def create_clinic(clinic_data: Dict[str, Any]) -> Clinic:
        """
        Tạo clinic mới
        
        Args:
            clinic_data: Dictionary chứa data
                {
                    "name": str,
                    "address": str,
                    "is_active": bool
                }
        
        Returns:
            Clinic: Clinic vừa tạo
        """
        return Clinic.objects.create(**clinic_data)
    
    @staticmethod
    @transaction.atomic
    def update_clinic(
        clinic_id: int, 
        update_data: Dict[str, Any]
    ) -> Clinic:
        """
        Cập nhật clinic
        
        Args:
            clinic_id: ID của clinic cần update
            update_data: Dictionary chứa fields cần update
                {
                    "name": str (optional),
                    "address": str (optional),
                    "is_active": bool (optional)
                }
        
        Returns:
            Clinic: Clinic đã update
        """
        clinic = Clinic.objects.get(id=clinic_id)
        for key, value in update_data.items():
            setattr(clinic, key, value)
        clinic.save()
        return clinic
    
    @staticmethod
    @transaction.atomic
    def delete_clinic(clinic_id: int) -> bool:
        """
        Xóa clinic
        
        Args:
            clinic_id: ID của clinic cần xóa
        
        Returns:
            bool: True nếu xóa thành công
        """
        Clinic.objects.filter(id=clinic_id).delete()
        return True
```

### **Ví dụ 2: Complex Types**

```python
from typing import List, Dict, Tuple, Optional, Any

def get_clinic_statistics() -> Dict[str, int]:
    """
    Returns: Dictionary với key là string, value là int
    {"total": 10, "active": 8, "inactive": 2}
    """
    return {
        'total': Clinic.objects.count(),
        'active': Clinic.objects.filter(is_active=True).count(),
        'inactive': Clinic.objects.filter(is_active=False).count(),
    }

def batch_create_clinics(
    clinics_data: List[Dict[str, Any]]
) -> List[Clinic]:
    """
    Tạo nhiều clinics cùng lúc
    
    Args:
        clinics_data: Danh sách dictionary
        [
            {"name": "Clinic 1", "address": "Address 1"},
            {"name": "Clinic 2", "address": "Address 2"}
        ]
    
    Returns:
        List[Clinic]: Danh sách Clinic objects đã tạo
    """
    clinics = [Clinic(**data) for data in clinics_data]
    return Clinic.objects.bulk_create(clinics)

def find_clinic_with_details(
    clinic_id: int
) -> Tuple[Clinic, int, bool]:
    """
    Returns: Tuple (clinic_object, patient_count, has_doctors)
    """
    clinic = Clinic.objects.get(id=clinic_id)
    patient_count = clinic.patients.count()
    has_doctors = clinic.doctors.exists()
    return (clinic, patient_count, has_doctors)
```

---

## 🔥 Best Practices

### ✅ **ĐÚNG:**

```python
from typing import Optional, Dict, Any
from django.db.models import QuerySet

def get_clinics(
    is_active: Optional[bool] = None
) -> QuerySet[Clinic]:
    """Clear type hints"""
    pass

def update_clinic(
    clinic_id: int, 
    data: Dict[str, Any]
) -> Clinic:
    """Dict[str, Any] = flexible dictionary"""
    pass
```

### ❌ **SAI:**

```python
# Không có type hints
def get_clinics(is_active=None):
    pass

# Sai cú pháp
def update_clinic(clinic_id: int, data: dict) -> object:
    # Nên dùng Dict[str, Any] thay vì dict
    # Nên dùng Clinic thay vì object
    pass
```

---

## 🛠️ Type Checking Tools

### **1. mypy** (Recommended)

```bash
# Install
pip install mypy

# Check
mypy apps/users/services/
```

### **2. Pylance** (VS Code)

```json
// settings.json
{
    "python.analysis.typeCheckingMode": "basic"  // hoặc "strict"
}
```

---

## 📖 Common Types Reference

| Type Hint | Ý nghĩa | Ví dụ |
|-----------|---------|-------|
| `str` | String | `"hello"` |
| `int` | Integer | `123` |
| `bool` | Boolean | `True`, `False` |
| `float` | Float | `3.14` |
| `List[str]` | List of strings | `["a", "b"]` |
| `Dict[str, int]` | Dict với key=str, value=int | `{"age": 25}` |
| `Dict[str, Any]` | Dict với value bất kỳ | `{"name": "A", "age": 25}` |
| `Optional[int]` | int hoặc None | `123` hoặc `None` |
| `Union[int, str]` | int HOẶC str | `123` hoặc `"abc"` |
| `Tuple[str, int]` | Tuple cố định | `("name", 123)` |
| `QuerySet[Model]` | Django QuerySet | `Model.objects.all()` |
| `Any` | Bất kỳ kiểu nào | Dùng khi không biết trước |

---

## 🎓 Tóm tắt

**Type Hints trong Service Layer:**

```python
from typing import Optional, Dict, Any, List
from django.db.models import QuerySet
from apps.users.models import Clinic

class ClinicService:
    @staticmethod
    def method_name(
        param1: int,                      # Bắt buộc, kiểu int
        param2: Optional[str] = None,     # Optional, mặc định None
        param3: Dict[str, Any] = {}       # Dict, mặc định {}
    ) -> QuerySet[Clinic]:                # Return QuerySet of Clinic
        """Docstring giải thích"""
        pass
```

**Lợi ích:**
- ✅ IDE autocomplete (Ctrl+Space)
- ✅ Phát hiện lỗi type sớm
- ✅ Code dễ đọc, dễ maintain
- ✅ Tự động generate documentation

**Lưu ý:**
- Type hints chỉ là **gợi ý**, không **ép buộc** runtime
- Dùng `mypy` để check types trước khi commit
- `Dict[str, Any]` là lựa chọn tốt cho flexible data
- `Optional[T]` = `Union[T, None]`

---

## 📚 Tài liệu tham khảo

- **Python typing**: https://docs.python.org/3/library/typing.html
- **Django QuerySet types**: https://github.com/typeddjango/django-stubs
- **mypy**: https://mypy.readthedocs.io/
- **PEP 484**: https://www.python.org/dev/peps/pep-0484/
