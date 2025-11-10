# ═══════════════════════════════════════════════════════════════
# MIGRATION SCRIPT - Tự động migrate sang CustomUser
# ═══════════════════════════════════════════════════════════════

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       AUTO MIGRATION - CustomUser Setup (Development)       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra xem có muốn tiếp tục không
Write-Host "⚠️  LƯU Ý: Script này sẽ XÓA database hiện tại!" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Bạn có chắc chắn muốn tiếp tục? (y/N)"

if ($confirm -ne "y") {
    Write-Host "❌ Đã hủy!" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 BƯỚC 1: XÓA VÀ TẠO LẠI DATABASE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$mysqlUser = "root"
$mysqlPassword = "hocmysql1234"
$dbName = "kiosk_2"

Write-Host "Đang xóa database $dbName..." -ForegroundColor Yellow

# Tạo SQL commands
$sqlCommands = @"
DROP DATABASE IF EXISTS $dbName;
CREATE DATABASE $dbName CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"@

# Thực thi MySQL commands
$sqlCommands | mysql -u $mysqlUser -p$mysqlPassword 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database đã được tạo lại thành công!" -ForegroundColor Green
} else {
    Write-Host "❌ Lỗi khi tạo database!" -ForegroundColor Red
    Write-Host "Vui lòng tạo database thủ công:" -ForegroundColor Yellow
    Write-Host "  DROP DATABASE IF EXISTS $dbName;" -ForegroundColor White
    Write-Host "  CREATE DATABASE $dbName;" -ForegroundColor White
    exit
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 BƯỚC 2: XÓA MIGRATION FILES CŨ" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "Đang xóa migration files..." -ForegroundColor Yellow

# Xóa migration files trong apps/kiosk/migrations/ (giữ __init__.py)
Get-ChildItem -Path "apps\kiosk\migrations\*.py" -Exclude "__init__.py" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "apps\kiosk\migrations\__pycache__" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue

# Xóa migration files trong apps/authentication/migrations/ (giữ __init__.py)
Get-ChildItem -Path "apps\authentication\migrations\*.py" -Exclude "__init__.py" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "apps\authentication\migrations\__pycache__" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue

Write-Host "✅ Migration files đã được xóa!" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 BƯỚC 3: TẠO MIGRATIONS MỚI" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "Đang tạo migrations..." -ForegroundColor Yellow
python manage.py makemigrations

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migrations đã được tạo!" -ForegroundColor Green
} else {
    Write-Host "❌ Lỗi khi tạo migrations!" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 BƯỚC 4: APPLY MIGRATIONS" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "Đang apply migrations..." -ForegroundColor Yellow
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migrations đã được apply thành công!" -ForegroundColor Green
} else {
    Write-Host "❌ Lỗi khi apply migrations!" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 BƯỚC 5: TẠO SUPERUSER" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "Đang tạo superuser tự động..." -ForegroundColor Yellow

# Tạo script Python để tạo superuser tự động
$pythonScript = @"
from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role='admin',
        first_name='Admin',
        last_name='User'
    )
    print('✅ Superuser đã được tạo!')
    print('   Username: admin')
    print('   Password: admin123')
else:
    print('⚠️  Superuser đã tồn tại!')
"@

# Lưu script vào file tạm
$pythonScript | Out-File -FilePath "create_superuser_temp.py" -Encoding UTF8

# Chạy script
python create_superuser_temp.py

# Xóa file tạm
Remove-Item "create_superuser_temp.py" -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 HOÀN THÀNH!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ CustomUser đã được setup thành công!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 THÔNG TIN ĐĂNG NHẬP:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host "   Email: admin@example.com" -ForegroundColor White
Write-Host ""
Write-Host "🚀 TIẾP THEO:" -ForegroundColor Cyan
Write-Host "   1. Chạy server: python manage.py runserver" -ForegroundColor White
Write-Host "   2. Truy cập Admin: http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host "   3. Test API: http://127.0.0.1:8000/api/users/" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
