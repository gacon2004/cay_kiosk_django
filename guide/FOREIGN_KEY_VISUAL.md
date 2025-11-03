# Foreign Key Visual Examples

## 📊 Quan hệ 1-N (One-to-Many)

```
┌─────────────────────┐              ┌─────────────────────┐
│     Patients        │              │     Insurance       │
│     (Model Cha)     │ 1        N   │     (Model Con)     │
├─────────────────────┤ ───────────► ├─────────────────────┤
│ id (PK)             │              │ id (PK)             │
│ national_id         │              │ patient_id (FK)     │◄─┐
│ full_name           │              │ insurance_number    │  │
│ date_of_birth       │              │ expiry_date         │  │
│ phone               │              │ issued_date         │  │
└─────────────────────┘              └─────────────────────┘  │
                                              │                 │
                                              └─────────────────┘
                                              Foreign Key
                                              references Patients.id
```

## 💡 Ví dụ Data

### **Bảng Patients (Cha):**
```
┌────┬─────────────┬──────────────┬────────────┐
│ id │ national_id │  full_name   │    phone   │
├────┼─────────────┼──────────────┼────────────┤
│ 1  │ 001234567890│ Nguyễn Văn A │ 0901234567 │
│ 2  │ 002345678901│ Trần Thị B   │ 0912345678 │
│ 3  │ 003456789012│ Lê Văn C     │ 0923456789 │
└────┴─────────────┴──────────────┴────────────┘
```

### **Bảng Insurance (Con):**
```
┌────┬────────────┬──────────────────┬─────────────┐
│ id │ patient_id │ insurance_number │ expiry_date │
├────┼────────────┼──────────────────┼─────────────┤
│ 1  │     1      │   BH001234567    │ 2025-12-31  │ ◄─┐
│ 2  │     1      │   BH001234568    │ 2026-06-30  │   ├─ Cả 2 thuộc Patient 1
│ 3  │     2      │   BH002345678    │ 2025-11-30  │   │
│ 4  │     3      │   BH003456789    │ 2026-01-31  │   │
└────┴────────────┴──────────────────┴─────────────┘   │
       │                                                  │
       └──────────────────────────────────────────────────┘
       Foreign Key trỏ đến Patients.id
```

## 🔍 Các hành động on_delete

### **1. CASCADE (Xóa cha → Xóa con):**

```python
patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
```

```
TRƯỚC:                           SAU khi xóa Patient 1:
┌─────────────┐                  ┌─────────────┐
│ Patient     │                  │ Patient     │
├─────────────┤                  ├─────────────┤
│ 1: Văn A    │ ◄─┐              │ 2: Thị B    │
│ 2: Thị B    │   │              │ 3: Văn C    │
│ 3: Văn C    │   │              └─────────────┘
└─────────────┘   │
                  │              ┌─────────────┐
┌─────────────┐   │              │ Insurance   │
│ Insurance   │   │              ├─────────────┤
├─────────────┤   │              │ 3: BH002... │
│ 1: BH001... │───┘              │ 4: BH003... │
│ 2: BH001... │───┘ ← BỊ XÓA     └─────────────┘
│ 3: BH002... │
│ 4: BH003... │
└─────────────┘
```

### **2. PROTECT (Bảo vệ - Không cho xóa):**

```python
patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
```

```
Khi cố xóa Patient 1:
┌─────────────┐
│ Patient     │
├─────────────┤
│ 1: Văn A    │ ◄─── ❌ LỖI! Không thể xóa
│ 2: Thị B    │       vì còn Insurance tham chiếu
│ 3: Văn C    │
└─────────────┘
       ▲
       │
       │ FK references
       │
┌─────────────┐
│ Insurance   │
├─────────────┤
│ 1: BH001... │─── còn tham chiếu đến Patient 1
│ 2: BH001... │
└─────────────┘
```

### **3. SET_NULL (Set NULL):**

```python
patient = models.ForeignKey(
    Patient, 
    on_delete=models.SET_NULL, 
    null=True
)
```

```
TRƯỚC:                           SAU khi xóa Patient 1:
┌─────────────┐                  ┌─────────────┐
│ Patient     │                  │ Patient     │
├─────────────┤                  ├─────────────┤
│ 1: Văn A    │ ◄─┐              │ 2: Thị B    │
│ 2: Thị B    │   │              │ 3: Văn C    │
│ 3: Văn C    │   │              └─────────────┘
└─────────────┘   │
                  │              ┌─────────────┐
┌─────────────┐   │              │ Insurance   │
│ Insurance   │   │              ├─────────────┤
├─────────────┤   │              │ 1: NULL     │ ← Set thành NULL
│ 1: patient=1│───┘              │ 2: NULL     │
│ 2: patient=1│───┘              │ 3: patient=2│
│ 3: patient=2│                  │ 4: patient=3│
│ 4: patient=3│                  └─────────────┘
└─────────────┘
```

## 🔄 Forward & Reverse Relations

### **Forward Relation (Con → Cha):**

```python
# Insurance → Patient
insurance = Insurance.objects.get(id=1)
patient = insurance.patient_id  # Truy cập trực tiếp

print(patient.full_name)  # "Nguyễn Văn A"
```

```
┌─────────────────┐
│ Insurance (id=1)│
│ patient_id = 1  │───┐
└─────────────────┘   │
                      ▼
                 ┌─────────────┐
                 │ Patient(id=1)│
                 │ Nguyễn Văn A│
                 └─────────────┘
```

### **Reverse Relation (Cha → Con):**

```python
# Patient → Insurance (qua related_name)
patient = Patient.objects.get(id=1)
insurances = patient.insurances.all()  # QuerySet

for ins in insurances:
    print(ins.insurance_number)
```

```
┌─────────────────┐
│ Patient (id=1)  │
│ Nguyễn Văn A    │
└─────────────────┘
        │
        │ .insurances.all()
        │
        ▼
┌───────────────────────────┐
│ Insurance (patient_id=1)  │
├───────────────────────────┤
│ 1: BH001234567            │
│ 2: BH001234568            │
└───────────────────────────┘
```

## 📊 Query Performance

### **❌ N+1 Problem:**

```python
# BAD: 1 query lấy insurances + N queries lấy patient
insurances = Insurance.objects.all()  # 1 query
for insurance in insurances:
    print(insurance.patient_id.full_name)  # N queries!
    
# Tổng: 1 + N queries
```

```
Query 1: SELECT * FROM insurance;
Query 2: SELECT * FROM patient WHERE id=1;  ← Patient cho Insurance 1
Query 3: SELECT * FROM patient WHERE id=1;  ← Patient cho Insurance 2
Query 4: SELECT * FROM patient WHERE id=2;  ← Patient cho Insurance 3
Query 5: SELECT * FROM patient WHERE id=3;  ← Patient cho Insurance 4
...
```

### **✅ select_related (Optimized):**

```python
# GOOD: 1 query với JOIN
insurances = Insurance.objects.select_related('patient_id')
for insurance in insurances:
    print(insurance.patient_id.full_name)  # Không query thêm!
    
# Tổng: 1 query
```

```
Query: 
SELECT insurance.*, patient.* 
FROM insurance 
LEFT JOIN patient ON insurance.patient_id = patient.id;

┌───────────────────────────────────────────┐
│ Result (1 query - đã có cả data)         │
├───────────────────────────────────────────┤
│ Insurance 1 + Patient A (full data)       │
│ Insurance 2 + Patient A (full data)       │
│ Insurance 3 + Patient B (full data)       │
│ Insurance 4 + Patient C (full data)       │
└───────────────────────────────────────────┘
```

## 🎯 Use Cases

### **1. Blog System:**
```
Post (1) ─────► Comment (N)
author_id       post_id
```

### **2. E-commerce:**
```
Customer (1) ───► Order (N) ───► OrderItem (N)
                  customer_id      order_id
```

### **3. Healthcare (Your project):**
```
Patient (1) ────► Insurance (N)
                  patient_id
                  
Patient (1) ────► Appointment (N)
                  patient_id
                  
Doctor (1) ─────► Appointment (N)
                  doctor_id
```

## 📝 Cheat Sheet

```python
# Khai báo
parent = models.ForeignKey(
    Parent, 
    on_delete=models.CASCADE,
    related_name='children'
)

# Sử dụng
child.parent          # Forward: Con → Cha
parent.children.all() # Reverse: Cha → Con

# Tối ưu
.select_related('parent')      # Forward (ForeignKey)
.prefetch_related('children')  # Reverse (related_name)

# Filter
Child.objects.filter(parent__name='A')  # Lookup
Parent.objects.filter(children__id=1)   # Reverse lookup
```
