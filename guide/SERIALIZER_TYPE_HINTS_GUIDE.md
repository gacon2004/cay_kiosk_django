# Type Hints Guide for Django REST Framework Serializers

## 📚 Giới thiệu

Type hints trong **DRF Serializers** giúp:
- ✅ IDE autocomplete cho validate methods
- ✅ Phát hiện lỗi type sớm
- ✅ Code dễ đọc, dễ maintain
- ✅ Documentation rõ ràng hơn

---

## 🎯 Cấu trúc Serializer với Type Hints

### **1. Import types**

```python
from typing import Any, Dict, Optional, List
from rest_framework import serializers
from apps.users.models import Clinic, Insurance
```

---

## 📝 Type Hints cho Serializer Methods

### **1. validate_<field_name> Methods**

Validate từng field cụ thể:

```python
class ClinicSerializer(serializers.ModelSerializer):
    
    def validate_name(self, value: str) -> str:
        """
        Validate tên phòng khám
        
        Args:
            value: Giá trị field 'name' cần validate (type tùy field)
        
        Returns:
            str: Giá trị đã validate (cùng type với input)
        
        Raises:
            ValidationError: Nếu không hợp lệ
        """
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên không được trống")
        return value
    
    def validate_email(self, value: str) -> str:
        """Validate email field"""
        if '@' not in value:
            raise serializers.ValidationError("Email không hợp lệ")
        return value.lower()
    
    def validate_age(self, value: int) -> int:
        """Validate age field"""
        if value < 0 or value > 150:
            raise serializers.ValidationError("Tuổi không hợp lệ")
        return value
    
    def validate_is_active(self, value: bool) -> bool:
        """Validate boolean field"""
        return value
```

**Quy tắc:**
- Input type = Field type trong Model
- Return type = Cùng type với input
- Method name: `validate_<field_name>`

---

### **2. validate() Method (Validate nhiều fields)**

Validate cross-field (nhiều fields cùng lúc):

```python
class InsuranceSerializer(serializers.ModelSerializer):
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate toàn bộ data (cross-field validation)
        
        Args:
            data: Dictionary chứa tất cả validated data
                {
                    "field1": value1,
                    "field2": value2,
                    ...
                }
        
        Returns:
            Dict[str, Any]: Data đã validate
        
        Raises:
            ValidationError: Nếu không hợp lệ
        """
        # Validate issued_date < expiry_date
        if data.get('issued_date') and data.get('expiry_date'):
            if data['issued_date'] >= data['expiry_date']:
                raise serializers.ValidationError({
                    'issued_date': 'Ngày cấp phải nhỏ hơn ngày hết hạn'
                })
        
        return data
```

**Quy tắc:**
- Input: `Dict[str, Any]` (dictionary với values bất kỳ)
- Return: `Dict[str, Any]` (cùng type)
- Validate logic giữa nhiều fields

---

### **3. SerializerMethodField**

Custom field được tính toán:

```python
from typing import Dict, Any, Optional

class InsuranceSerializer(serializers.ModelSerializer):
    
    # Khai báo field
    patient = serializers.SerializerMethodField(read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    
    def get_patient(self, obj: Insurance) -> Dict[str, Any]:
        """
        Lấy thông tin bệnh nhân (cho SerializerMethodField)
        
        Args:
            obj: Instance của Model (Insurance)
        
        Returns:
            Dict[str, Any]: Dictionary chứa data custom
        """
        return {
            'id': obj.patient_id.id,
            'full_name': obj.patient_id.full_name,
        }
    
    def get_days_until_expiry(self, obj: Insurance) -> Optional[int]:
        """
        Tính số ngày đến expiry
        
        Args:
            obj: Insurance instance
        
        Returns:
            Optional[int]: Số ngày, hoặc None
        """
        return obj.days_until_expiry()
```

**Quy tắc:**
- Method name: `get_<field_name>`
- Input: Model instance (`obj: ModelClass`)
- Return: Bất kỳ type nào (Dict, str, int, List...)

---

### **4. to_representation() Method**

Override cách serialize data:

```python
class ClinicSerializer(serializers.ModelSerializer):
    
    def to_representation(self, instance: Clinic) -> Dict[str, Any]:
        """
        Customize output data
        
        Args:
            instance: Model instance cần serialize
        
        Returns:
            Dict[str, Any]: Data đã serialize
        """
        data = super().to_representation(instance)
        # Customize data
        data['name_upper'] = data['name'].upper()
        return data
```

---

### **5. to_internal_value() Method**

Override cách deserialize data:

```python
class ClinicSerializer(serializers.ModelSerializer):
    
    def to_internal_value(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Customize input data trước khi validate
        
        Args:
            data: Raw input data từ request
        
        Returns:
            Dict[str, Any]: Data đã xử lý
        """
        # Pre-process data
        if 'name' in data:
            data['name'] = data['name'].strip()
        
        return super().to_internal_value(data)
```

---

### **6. create() & update() Methods**

```python
from django.db import transaction

class ClinicSerializer(serializers.ModelSerializer):
    
    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Clinic:
        """
        Tạo instance mới
        
        Args:
            validated_data: Data đã validate
        
        Returns:
            Clinic: Instance vừa tạo
        """
        return Clinic.objects.create(**validated_data)
    
    @transaction.atomic
    def update(
        self, 
        instance: Clinic, 
        validated_data: Dict[str, Any]
    ) -> Clinic:
        """
        Update instance
        
        Args:
            instance: Instance cần update
            validated_data: Data mới đã validate
        
        Returns:
            Clinic: Instance đã update
        """
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
```

---

## 🔥 Ví dụ đầy đủ

### **Insurance Serializer với Type Hints:**

```python
from typing import Dict, Any, Optional
from datetime import date
from rest_framework import serializers
from apps.users.models import Insurance, Patients


class InsuranceSerializer(serializers.ModelSerializer):
    """Serializer cho bảo hiểm y tế"""
    
    # SerializerMethodFields
    patient = serializers.SerializerMethodField(read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = Insurance
        fields = [
            'id', 'patient', 'insurance_number', 
            'expiry_date', 'issued_date', 'days_until_expiry'
        ]
        read_only_fields = ('id',)
    
    def get_patient(self, obj: Insurance) -> Dict[str, Any]:
        """Lấy thông tin bệnh nhân"""
        return {
            'id': obj.patient_id.id,
            'full_name': obj.patient_id.full_name,
        }
    
    def get_days_until_expiry(self, obj: Insurance) -> Optional[int]:
        """Số ngày còn lại"""
        return obj.days_until_expiry()
    
    def validate_insurance_number(self, value: str) -> str:
        """Validate số thẻ BHYT"""
        if len(value) < 10:
            raise serializers.ValidationError("Số thẻ không hợp lệ")
        return value.upper()
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate cross-field"""
        if 'expiry_date' in data and data['expiry_date'] < date.today():
            raise serializers.ValidationError({
                'expiry_date': 'Ngày hết hạn đã qua'
            })
        
        if 'issued_date' in data and 'expiry_date' in data:
            if data['issued_date'] >= data['expiry_date']:
                raise serializers.ValidationError({
                    'issued_date': 'Ngày cấp phải nhỏ hơn ngày hết hạn'
                })
        
        return data
```

---

## 📊 Type Hints Reference cho Serializers

| Method | Input Type | Return Type | Mục đích |
|--------|-----------|-------------|----------|
| `validate_<field>` | Field type (str, int, bool...) | Cùng field type | Validate 1 field |
| `validate()` | `Dict[str, Any]` | `Dict[str, Any]` | Validate nhiều fields |
| `get_<field>` | Model instance | Any type | SerializerMethodField |
| `to_representation()` | Model instance | `Dict[str, Any]` | Customize output |
| `to_internal_value()` | `Dict[str, Any]` | `Dict[str, Any]` | Customize input |
| `create()` | `Dict[str, Any]` | Model instance | Tạo mới |
| `update()` | Model instance, `Dict[str, Any]` | Model instance | Cập nhật |

---

## 🎯 Field Types trong Model vs Serializer

| Model Field | Python Type | Ví dụ |
|-------------|-------------|-------|
| `CharField` | `str` | `"Hello"` |
| `IntegerField` | `int` | `123` |
| `BooleanField` | `bool` | `True`, `False` |
| `DateField` | `date` | `date(2025, 11, 3)` |
| `DateTimeField` | `datetime` | `datetime.now()` |
| `DecimalField` | `Decimal` | `Decimal("99.99")` |
| `FloatField` | `float` | `3.14` |
| `JSONField` | `Dict[str, Any]` | `{"key": "value"}` |
| `ForeignKey` | Model instance | `Patient.objects.get(id=1)` |

---

## ✅ Best Practices

### **1. Luôn khai báo type cho validate methods:**

```python
# ✅ ĐÚNG
def validate_name(self, value: str) -> str:
    return value.strip()

# ❌ SAI
def validate_name(self, value):
    return value.strip()
```

### **2. Dùng Dict[str, Any] cho validate():**

```python
# ✅ ĐÚNG - Flexible
def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
    pass

# ❌ KHÔNG CẦN - Quá cụ thể
def validate(self, data: Dict[str, Union[str, int, bool]]) -> Dict[str, Any]:
    pass
```

### **3. Dùng Optional khi có thể None:**

```python
# ✅ ĐÚNG
def get_days_until_expiry(self, obj: Insurance) -> Optional[int]:
    result = obj.calculate_days()
    return result  # Có thể None

# ❌ SAI - Không xử lý None
def get_days_until_expiry(self, obj: Insurance) -> int:
    return obj.calculate_days()  # Có thể None!
```

### **4. Type hint cho SerializerMethodField:**

```python
class MySerializer(serializers.ModelSerializer):
    custom_field = serializers.SerializerMethodField()
    
    # ✅ ĐÚNG
    def get_custom_field(self, obj: MyModel) -> Dict[str, Any]:
        return {'key': 'value'}
    
    # ❌ SAI
    def get_custom_field(self, obj):
        return {'key': 'value'}
```

---

## 🛠️ IDE Support

Với type hints đầy đủ, IDE sẽ:

```python
# Autocomplete khi type
data: Dict[str, Any] = {...}
data.  # ← IDE gợi ý: .get(), .keys(), .values(), etc.

# Type checking
value: str = self.validate_name("test")
value.  # ← IDE gợi ý: .upper(), .lower(), .strip(), etc.

# Error detection
def validate_age(self, value: int) -> str:  # ❌ IDE cảnh báo!
    return value  # Return int nhưng khai báo str
```

---

## 📚 Tài liệu tham khảo

- **DRF Serializers**: https://www.django-rest-framework.org/api-guide/serializers/
- **Python typing**: https://docs.python.org/3/library/typing.html
- **DRF Validation**: https://www.django-rest-framework.org/api-guide/validators/

---

## 🎓 Tóm tắt

**Type Hints cho Serializers:**

```python
from typing import Dict, Any, Optional
from rest_framework import serializers

class MySerializer(serializers.ModelSerializer):
    
    # 1. Validate single field
    def validate_<field>(self, value: FieldType) -> FieldType:
        """Field type depends on Model field type"""
        return processed_value
    
    # 2. Validate multiple fields
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Always Dict[str, Any]"""
        return data
    
    # 3. SerializerMethodField
    def get_<field>(self, obj: ModelClass) -> AnyType:
        """obj = Model instance, return any type"""
        return result
    
    # 4. Create/Update
    def create(self, validated_data: Dict[str, Any]) -> ModelClass:
        return ModelClass.objects.create(**validated_data)
```

**Nhớ:**
- `validate_<field>`: Input/Output cùng type
- `validate()`: `Dict[str, Any]` → `Dict[str, Any]`
- `get_<field>`: Model instance → Any type
- Luôn import types: `from typing import Dict, Any, Optional`
