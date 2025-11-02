# ================================
# GHI CHÚ VỀ MÔ HÌNH MVC TRONG DJANGO REST FRAMEWORK
# ================================

"""
📚 MÔ HÌNH MVC TRONG DJANGO:

Django sử dụng mô hình MTV (Model-Template-View) nhưng có thể ánh xạ sang MVC:

┌─────────────────┬──────────────────────┬─────────────────────────────────┐
│  MVC Pattern    │  Django/DRF Pattern  │  File tương ứng                 │
├─────────────────┼──────────────────────┼─────────────────────────────────┤
│  Model          │  Model               │  models.py                      │
│  (Dữ liệu)      │  (Business Logic)    │  - Định nghĩa cấu trúc DB       │
│                 │                      │  - Validation logic             │
│                 │                      │  - Business methods             │
├─────────────────┼──────────────────────┼─────────────────────────────────┤
│  View           │  Template (Web)      │  serializers.py (REST API)      │
│  (Hiển thị)     │  Serializer (API)    │  - Chuyển đổi data <-> JSON     │
│                 │                      │  - Validation data input        │
│                 │                      │  - Format output                │
├─────────────────┼──────────────────────┼─────────────────────────────────┤
│  Controller     │  View + URLconf      │  views.py + urls.py             │
│  (Logic điều    │  (Request Handler)   │  - Xử lý HTTP requests          │
│   khiển)        │                      │  - Business logic               │
│                 │                      │  - Trả về responses             │
└─────────────────┴──────────────────────┴─────────────────────────────────┘

🎯 CẤU TRÚC THƯ MỤC THEO MVC:

apps/
├── authentication/
│   ├── models/              # ← MODEL LAYER (nếu có custom user model)
│   │   ├── __init__.py
│   │   └── user.py
│   │
│   ├── serializers/         # ← VIEW LAYER (Data representation)
│   │   ├── __init__.py
│   │   ├── auth_serializer.py
│   │   └── profile_serializer.py
│   │
│   ├── views/              # ← CONTROLLER LAYER (Business logic)
│   │   ├── __init__.py
│   │   ├── register_view.py
│   │   ├── login_view.py
│   │   ├── profile_view.py
│   │   └── password_view.py
│   │
│   ├── services/           # ← SERVICE LAYER (Optional - complex logic)
│   │   ├── __init__.py
│   │   └── auth_service.py
│   │
│   └── urls.py             # ← ROUTING (URL mapping)
│
└── users/
    ├── models/             # ← MODEL LAYER
    │   ├── __init__.py
    │   ├── patient.py
    │   ├── doctor.py
    │   └── insurance.py
    │
    ├── serializers/        # ← VIEW LAYER
    │   ├── __init__.py
    │   ├── patient_serializer.py
    │   ├── doctor_serializer.py
    │   └── insurance_serializer.py
    │
    ├── views/             # ← CONTROLLER LAYER
    │   ├── __init__.py
    │   ├── patient_view.py
    │   ├── doctor_view.py
    │   └── user_view.py
    │
    ├── services/          # ← SERVICE LAYER (Business logic phức tạp)
    │   ├── __init__.py
    │   ├── patient_service.py
    │   └── insurance_service.py
    │
    └── urls.py            # ← ROUTING

📋 NGUYÊN TẮC PHÂN TÁCH:

1. **models/** (MODEL - Tầng dữ liệu)
   - Định nghĩa cấu trúc database
   - Các phương thức liên quan đến data
   - Validation ở cấp độ model
   - Không chứa business logic phức tạp

2. **serializers/** (VIEW - Tầng biểu diễn dữ liệu)
   - Chuyển đổi Model <-> JSON
   - Validation input data
   - Custom field serialization
   - Nested serializers

3. **views/** (CONTROLLER - Tầng điều khiển)
   - Xử lý HTTP requests (GET, POST, PUT, DELETE)
   - Gọi serializers để validate data
   - Gọi services để xử lý logic phức tạp
   - Trả về responses
   - Authentication & Permission checks

4. **services/** (SERVICE - Tầng logic nghiệp vụ - Optional)
   - Business logic phức tạp
   - Tương tác với nhiều models
   - External API calls
   - Email, SMS, Payment processing
   - Tính toán phức tạp

5. **urls.py** (ROUTING)
   - Map URLs tới views
   - URL patterns
   - API versioning

🔧 THƯ MỤC PHỤ TRỢ:

core/
├── permissions.py          # Custom permissions
├── pagination.py          # Custom pagination
├── exceptions.py          # Custom exceptions
└── middleware.py          # Custom middleware

utils/
├── helpers.py             # Helper functions
├── validators.py          # Custom validators
├── decorators.py          # Custom decorators
└── constants.py           # Constants

"""

# ================================
# LỆNH CHẠY SERVER
# ================================

# Khởi động Django development server
# python manage.py runserver

# Chạy migrations
# python manage.py makemigrations
# python manage.py migrate

# Tạo superuser
# python manage.py createsuperuser

# Chạy tests
# python manage.py test

# Thu thập static files
# python manage.py collectstatic 