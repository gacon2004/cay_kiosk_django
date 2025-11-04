"""
MIGRATION SCRIPT - Chuyển từ User model cũ sang CustomUser
Script này giúp migrate data an toàn
"""

# ⚠️ QUAN TRỌNG: Đọc kỹ hướng dẫn trước khi chạy!

print("""
╔══════════════════════════════════════════════════════════════╗
║          MIGRATION SCRIPT - CustomUser Setup                 ║
╚══════════════════════════════════════════════════════════════╝

⚠️  LƯU Ý QUAN TRỌNG:

1. Script này sẽ XÓA database hiện tại và tạo mới
2. Chỉ dùng cho môi trường DEVELOPMENT
3. Backup data trước nếu cần giữ lại

═══════════════════════════════════════════════════════════════

📋 CÁC BƯỚC THỰC HIỆN:

OPTION 1: XÓA TOÀN BỘ VÀ TẠO MỚI (Development - Không có data quan trọng)
─────────────────────────────────────────────────────────────

1. Xóa database hiện tại:
   
   # MySQL
   DROP DATABASE kiosk_2;
   CREATE DATABASE kiosk_2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   # hoặc dùng script
   mysql -u root -p
   > DROP DATABASE kiosk_2;
   > CREATE DATABASE kiosk_2;
   > exit;

2. Xóa tất cả migration files (GIỮ LẠI __init__.py):
   
   # Windows PowerShell
   Get-ChildItem -Path "apps\\*\\migrations\\*.py" -Exclude "__init__.py" | Remove-Item
   
   # hoặc thủ công xóa các file trong:
   # apps/kiosk/migrations/ (giữ lại __init__.py)
   # apps/authentication/migrations/ (giữ lại __init__.py)

3. Tạo migrations mới:
   
   python manage.py makemigrations

4. Apply migrations:
   
   python manage.py migrate

5. Tạo superuser mới:
   
   python manage.py createsuperuser
   
   # Nhập thông tin:
   Username: admin
   Email: admin@example.com
   Password: admin123
   Password (again): admin123

6. Test server:
   
   python manage.py runserver
   # Truy cập: http://127.0.0.1:8000/admin/

═══════════════════════════════════════════════════════════════

OPTION 2: GIỮ DATA (Production - Có data quan trọng)
─────────────────────────────────────────────────────────────

⚠️  PHỨC TẠP HƠN - Cần kỹ năng migration nâng cao!

1. Backup data hiện tại:
   
   python manage.py dumpdata > backup.json

2. Tạo custom migration để chuyển data:
   
   python manage.py makemigrations --empty kiosk
   
   # Viết custom migration để:
   # - Tạo CustomUser table mới
   # - Copy data từ Users cũ sang CustomUser
   # - Update tất cả ForeignKey references

3. Apply migration:
   
   python manage.py migrate

4. Verify data:
   
   python manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> User.objects.all()
   >>> exit()

═══════════════════════════════════════════════════════════════

✅ SAU KHI MIGRATE THÀNH CÔNG:

1. Check CustomUser trong Admin:
   http://127.0.0.1:8000/admin/kiosk/customuser/

2. Test API endpoints:
   
   # List users
   curl http://127.0.0.1:8000/api/users/
   
   # Create user
   curl -X POST http://127.0.0.1:8000/api/users/ \\
     -H "Content-Type: application/json" \\
     -d '{
       "username": "doctor01",
       "email": "doctor@example.com",
       "password": "pass123",
       "password2": "pass123",
       "first_name": "Nguyễn",
       "last_name": "Văn A",
       "role": "doctor",
       "department": "Khoa Nội",
       "phone": "0901234567",
       "employee_id": "BS001"
     }'

3. Test Authentication:
   
   # Login
   curl -X POST http://127.0.0.1:8000/api/auth/login/ \\
     -H "Content-Type: application/json" \\
     -d '{
       "username": "doctor01",
       "password": "pass123"
     }'

═══════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING:

1. Lỗi "Table 'custom_users' already exists":
   → Xóa database và tạo lại từ đầu

2. Lỗi "AUTH_USER_MODEL refers to model 'kiosk.CustomUser' that has not been installed":
   → Check INSTALLED_APPS có 'apps.kiosk' chưa

3. Lỗi "No such column: custom_users.role":
   → Chạy lại makemigrations và migrate

4. Lỗi khi tạo superuser:
   → Tạo thủ công qua shell:
   
   python manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> user = User.objects.create_superuser(
   ...     username='admin',
   ...     email='admin@example.com',
   ...     password='admin123',
   ...     role='admin'
   ... )
   >>> exit()

═══════════════════════════════════════════════════════════════

📚 THÊM THÔNG TIN:

- File model: apps/kiosk/models/user.py
- File serializer: apps/kiosk/serializers/user_serializer.py
- File admin: apps/kiosk/admin.py
- Settings: config/settings.py (AUTH_USER_MODEL)

═══════════════════════════════════════════════════════════════
""")

import sys

choice = input("\n🚀 Bạn có muốn tiếp tục với OPTION 1 (Xóa database)? [y/N]: ")

if choice.lower() != 'y':
    print("\n❌ Đã hủy. Vui lòng backup data trước khi chạy script!")
    sys.exit(0)

print("\n✅ OK, bắt đầu migration...")
print("\n📝 Các bước tiếp theo:")
print("1. Mở MySQL và chạy: DROP DATABASE kiosk_2; CREATE DATABASE kiosk_2;")
print("2. Xóa migration files (giữ __init__.py)")
print("3. Chạy: python manage.py makemigrations")
print("4. Chạy: python manage.py migrate")
print("5. Chạy: python manage.py createsuperuser")
print("\n⚠️  Script này không tự động thực hiện các bước trên!")
print("    Vui lòng làm thủ công theo hướng dẫn.")
