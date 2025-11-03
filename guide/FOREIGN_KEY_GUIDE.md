# Django Foreign Key (Khóa Ngoại) - Hướng Dẫn Đầy Đủ

## 📚 Giới thiệu

**Foreign Key** là mối quan hệ **nhiều-một (Many-to-One)** giữa 2 models trong Django.

**Ví dụ thực tế:**
- Nhiều **Insurance** (Bảo hiểm) → Một **Patient** (Bệnh nhân)
- Nhiều **Comment** → Một **Post**
- Nhiều **Order** → Một **Customer**

---

## 🎯 Cú pháp cơ bản

### **1. Khai báo Foreign Key đơn giản:**

```python
from django.db import models

class Patient(models.Model):
    """Model cha (Parent)"""
    name = models.CharField(max_length=100)
    
class Insurance(models.Model):
    """Model con (Child) - có ForeignKey"""
    
    # ForeignKey trỏ đến Patient
    patient = models.ForeignKey(
        Patient,              # Model được tham chiếu
        on_delete=models.CASCADE,  # Hành động khi xóa
    )
    
    insurance_number = models.CharField(max_length=30)
```

**Giải thích:**
- `Patient` = Model cha (1 bệnh nhân)
- `Insurance` = Model con (nhiều bảo hiểm)
- Mỗi `Insurance` thuộc về 1 `Patient`
- 1 `Patient` có thể có nhiều `Insurance`

---

## 🔧 Các tham số của ForeignKey

### **Từ code của bạn (insurance.py):**

```python
class Insurance(models.Model):
    patient_id = models.ForeignKey(
        Patients,                    # 1. Model được tham chiếu
        on_delete=models.CASCADE,    # 2. Hành động khi xóa
        related_name="insurances",   # 3. Tên reverse relation
        verbose_name="Bệnh nhân",    # 4. Tên hiển thị (Admin)
    )
```

### **1. `to` (Model được tham chiếu):**

```python
# Cách 1: Truyền trực tiếp Model class
patient = models.ForeignKey(Patients, on_delete=models.CASCADE)

# Cách 2: Dùng string (nếu Model chưa được define)
patient = models.ForeignKey('Patients', on_delete=models.CASCADE)

# Cách 3: Tham chiếu Model từ app khác
patient = models.ForeignKey('users.Patients', on_delete=models.CASCADE)

# Cách 4: Self reference (tự tham chiếu)
parent = models.ForeignKey('self', on_delete=models.CASCADE)
```

### **2. `on_delete` (BẮT BUỘC):**

Hành động khi Model cha bị xóa:

```python
# CASCADE: Xóa luôn các bản ghi con
patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
# Xóa Patient → Xóa tất cả Insurance của Patient đó

# PROTECT: Ngăn không cho xóa nếu còn bản ghi con
patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
# Không thể xóa Patient nếu còn Insurance

# SET_NULL: Set NULL khi xóa (phải có null=True)
patient = models.ForeignKey(
    Patient, 
    on_delete=models.SET_NULL, 
    null=True
)
# Xóa Patient → Insurance.patient = NULL

# SET_DEFAULT: Set giá trị default (phải có default)
patient = models.ForeignKey(
    Patient,
    on_delete=models.SET_DEFAULT,
    default=1
)
# Xóa Patient → Insurance.patient = default value

# SET(): Set giá trị custom
def get_default_patient():
    return Patient.objects.get_or_create(name="Unknown")[0]

patient = models.ForeignKey(
    Patient,
    on_delete=models.SET(get_default_patient)
)

# DO_NOTHING: Không làm gì (có thể lỗi database)
patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
```

**Chọn on_delete nào?**
- ✅ `CASCADE`: Dùng nhiều nhất (xóa cha → xóa con)
- ✅ `PROTECT`: Khi cần bảo vệ data (không cho xóa cha nếu còn con)
- ✅ `SET_NULL`: Khi muốn giữ lại con nhưng remove quan hệ
- ❌ `DO_NOTHING`: Tránh dùng (có thể gây lỗi)

### **3. `related_name` (Tên reverse relation):**

```python
class Insurance(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='insurances'  # Tên reverse relation
    )
```

**Sử dụng:**
```python
# Forward relation (từ con → cha)
insurance = Insurance.objects.get(id=1)
patient = insurance.patient  # Truy cập Patient từ Insurance

# Reverse relation (từ cha → con)
patient = Patient.objects.get(id=1)
insurances = patient.insurances.all()  # Lấy tất cả Insurance của Patient
# Nếu không set related_name, mặc định là: patient.insurance_set.all()
```

**Best practices:**
```python
# ✅ ĐÚNG: Dùng số nhiều (vì 1 Patient có nhiều Insurance)
related_name='insurances'

# ❌ SAI: Dùng số ít
related_name='insurance'

# ✅ TỐT HƠN: Thêm prefix để tránh conflict
related_name='patient_insurances'
```

### **4. `null` và `blank`:**

```python
# null=True: Cho phép NULL trong database
# blank=True: Cho phép bỏ trống trong form/admin
patient = models.ForeignKey(
    Patient,
    on_delete=models.SET_NULL,
    null=True,      # Database có thể NULL
    blank=True,     # Form có thể bỏ trống
)

# null=False (default): Bắt buộc phải có giá trị
patient = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    null=False,  # Không được NULL (default)
)
```

### **5. `db_index`:**

```python
# Tự động tạo index trên database (mặc định True)
patient = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    db_index=True,  # Tăng tốc query (default)
)
```

### **6. `verbose_name` và `help_text`:**

```python
patient = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    verbose_name='Bệnh nhân',  # Tên hiển thị trong Admin
    help_text='Chọn bệnh nhân cho bảo hiểm này',  # Text gợi ý
)
```

---

## 💡 Ví dụ thực tế từ code của bạn

### **Model Insurance với ForeignKey:**

```python
# apps/users/models/insurance.py

from django.db import models
from .patient import Patients

class Insurance(models.Model):
    """
    Model Insurance (Con)
    Mỗi Insurance thuộc về 1 Patient
    1 Patient có thể có nhiều Insurance
    """
    
    # Foreign Key đến Patient
    patient_id = models.ForeignKey(
        Patients,                    # Model cha
        on_delete=models.CASCADE,    # Xóa Patient → Xóa Insurance
        related_name="insurances",   # patient.insurances.all()
        verbose_name="Bệnh nhân",    # Tên trong Admin
    )
    
    insurance_number = models.CharField(max_length=30, unique=True)
    expiry_date = models.DateField()
    issued_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.insurance_number} - {self.patient_id.full_name}"
```

### **Sử dụng trong code:**

```python
# 1. Tạo Insurance (Forward relation)
patient = Patients.objects.get(id=1)
insurance = Insurance.objects.create(
    patient_id=patient,  # Gán Patient
    insurance_number='BH123456',
    expiry_date='2025-12-31'
)

# 2. Truy cập Patient từ Insurance (Forward)
insurance = Insurance.objects.get(id=1)
patient_name = insurance.patient_id.full_name  # Truy cập field của Patient

# 3. Truy cập tất cả Insurance của Patient (Reverse)
patient = Patients.objects.get(id=1)
insurances = patient.insurances.all()  # QuerySet[Insurance]
# Hoặc: insurances = patient.insurances.filter(...)

# 4. Đếm số Insurance
count = patient.insurances.count()

# 5. Kiểm tra có Insurance không
has_insurance = patient.insurances.exists()

# 6. Lấy Insurance đầu tiên
first_insurance = patient.insurances.first()
```

---

## 🔄 Các loại quan hệ trong Django

### **1. One-to-Many (1-N) - ForeignKey:**

```python
class Patient(models.Model):
    name = models.CharField(max_length=100)

class Insurance(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # 1 Patient → Nhiều Insurance
```

### **2. Many-to-Many (N-N) - ManyToManyField:**

```python
class Doctor(models.Model):
    name = models.CharField(max_length=100)

class Patient(models.Model):
    name = models.CharField(max_length=100)
    doctors = models.ManyToManyField(Doctor, related_name='patients')
    # Nhiều Patient ↔ Nhiều Doctor
```

### **3. One-to-One (1-1) - OneToOneField:**

```python
class User(models.Model):
    username = models.CharField(max_length=100)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    # 1 User ↔ 1 UserProfile
```

---

## 📊 Query với ForeignKey

### **1. Filter theo ForeignKey:**

```python
# Lọc Insurance theo Patient ID
insurances = Insurance.objects.filter(patient_id=1)

# Lọc theo field của Patient (lookup)
insurances = Insurance.objects.filter(patient_id__full_name='Nguyễn Văn A')

# Lọc nhiều điều kiện
insurances = Insurance.objects.filter(
    patient_id__age__gte=18,
    patient_id__gender='Nam'
)
```

### **2. Select Related (Tối ưu query):**

```python
# ❌ BAD: N+1 queries
insurances = Insurance.objects.all()
for insurance in insurances:
    print(insurance.patient_id.full_name)  # Query mỗi lần loop

# ✅ GOOD: 1 query với JOIN
insurances = Insurance.objects.select_related('patient_id')
for insurance in insurances:
    print(insurance.patient_id.full_name)  # Không query thêm
```

### **3. Prefetch Related (Reverse relation):**

```python
# ✅ Tối ưu khi truy cập reverse relation
patients = Patients.objects.prefetch_related('insurances')
for patient in patients:
    for insurance in patient.insurances.all():  # Không query thêm
        print(insurance.insurance_number)
```

### **4. Annotate & Aggregate:**

```python
from django.db.models import Count

# Đếm số Insurance cho mỗi Patient
patients = Patients.objects.annotate(
    insurance_count=Count('insurances')
)

for patient in patients:
    print(f"{patient.full_name}: {patient.insurance_count} insurances")
```

---

## 🎨 ForeignKey trong Serializer

### **DRF Serializer với ForeignKey:**

```python
from rest_framework import serializers
from apps.users.models import Insurance, Patients

class InsuranceSerializer(serializers.ModelSerializer):
    
    # Cách 1: Hiển thị Patient object nested
    patient = serializers.SerializerMethodField(read_only=True)
    
    # Cách 2: Chấp nhận patient_id khi ghi
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patients.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = Insurance
        fields = ['id', 'patient', 'patient_id', 'insurance_number']
    
    def get_patient(self, obj):
        """Custom hiển thị Patient info"""
        return {
            'id': obj.patient_id.id,
            'full_name': obj.patient_id.full_name,
        }
```

**Request/Response:**
```json
// POST /api/insurances/ (Create)
{
    "patient_id": 1,
    "insurance_number": "BH123456"
}

// GET /api/insurances/1/ (Retrieve)
{
    "id": 1,
    "patient": {
        "id": 1,
        "full_name": "Nguyễn Văn A"
    },
    "insurance_number": "BH123456"
}
```

---

## ✅ Best Practices

### **1. Naming convention:**

```python
# ✅ ĐÚNG: Tên field rõ ràng
patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

# ❌ SAI: Thêm _id vào tên (Django tự động thêm)
patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
# Sẽ tạo field patient_id_id trong database!
```

**Lưu ý:** Trong code của bạn đang dùng `patient_id` - nên đổi thành `patient`:
```python
# Hiện tại (không tốt):
patient_id = models.ForeignKey(...)
# Database: patient_id_id

# Nên sửa thành:
patient = models.ForeignKey(...)
# Database: patient_id
```

### **2. Luôn set related_name:**

```python
# ✅ ĐÚNG
patient = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    related_name='insurances'  # Clear & explicit
)

# ❌ SAI: Không set (dùng default)
patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
# Phải dùng: patient.insurance_set.all() (ugly!)
```

### **3. Chọn on_delete phù hợp:**

```python
# ✅ CASCADE: Xóa cha → xóa con (common)
on_delete=models.CASCADE

# ✅ PROTECT: Không cho xóa cha nếu còn con (safety)
on_delete=models.PROTECT

# ✅ SET_NULL: Giữ con nhưng remove quan hệ
on_delete=models.SET_NULL, null=True
```

### **4. Index ForeignKey:**

```python
# ✅ ĐÚNG: Django tự động tạo index (default)
patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

# Hoặc explicit:
patient = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    db_index=True  # Tăng performance
)
```

### **5. Use select_related để tối ưu:**

```python
# ✅ ĐÚNG: Dùng select_related cho ForeignKey
insurances = Insurance.objects.select_related('patient').all()

# ❌ SAI: Không dùng → N+1 queries
insurances = Insurance.objects.all()
```

---

## 🚀 Migration với ForeignKey

### **Tạo ForeignKey:**

```python
# models.py
class Insurance(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
```

```bash
# 1. Tạo migration
python manage.py makemigrations

# 2. Xem SQL
python manage.py sqlmigrate users 0001

# 3. Apply vào database
python manage.py migrate
```

### **Thêm ForeignKey vào model đã có:**

```python
# Thêm field mới
patient = models.ForeignKey(
    Patient,
    on_delete=models.CASCADE,
    null=True,  # Cho phép NULL tạm thời
    blank=True
)
```

```bash
python manage.py makemigrations
# Django sẽ hỏi: Provide a one-off default now?
# Chọn 1 → Nhập giá trị default (hoặc None nếu null=True)

python manage.py migrate
```

---

## 📚 Tóm tắt

**ForeignKey = Quan hệ Nhiều-Một:**

```python
class Child(models.Model):
    parent = models.ForeignKey(
        Parent,                      # Model cha
        on_delete=models.CASCADE,    # Xóa cha → xóa con
        related_name='children',     # parent.children.all()
        verbose_name='Parent',       # Tên hiển thị
        null=False,                  # Bắt buộc
        db_index=True,               # Index (default)
    )
```

**Sử dụng:**
```python
# Forward: Child → Parent
child = Child.objects.get(id=1)
parent_name = child.parent.name

# Reverse: Parent → Children
parent = Parent.objects.get(id=1)
children = parent.children.all()

# Tối ưu query
children = Child.objects.select_related('parent')
parents = Parent.objects.prefetch_related('children')
```

**on_delete options:**
- `CASCADE`: Xóa cha → xóa con (common)
- `PROTECT`: Không cho xóa cha
- `SET_NULL`: Set NULL (cần null=True)
- `SET_DEFAULT`: Set default value

---

## 📖 Tài liệu tham khảo

- **Django ForeignKey**: https://docs.djangoproject.com/en/stable/ref/models/fields/#foreignkey
- **Model relationships**: https://docs.djangoproject.com/en/stable/topics/db/examples/
- **Query optimization**: https://docs.djangoproject.com/en/stable/topics/db/optimization/
