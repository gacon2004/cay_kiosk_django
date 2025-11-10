import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.kiosk.models import CustomUser

if not CustomUser.objects.filter(username="admin").exists():
    user = CustomUser.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin123",
        role="admin",
        first_name="System",
        last_name="Administrator",
    )
    print("✅ Superuser 'admin' created successfully!")
else:
    print("⚠️ Superuser 'admin' already exists.")

    """
    INSERT INTO services (name, is_active, description, prices_non_insurance, prices_insurance)
    VALUES
    ('Khám bệnh tổng quát', 1, 'Gói khám sức khỏe toàn diện bao gồm xét nghiệm cơ bản và chẩn đoán tổng quát.', 300000, 100000),
    ('Khám nội tổng quát', 1, 'Khám các cơ quan nội tạng: tim, gan, thận, phổi, tiêu hóa, nội tiết.', 250000, 80000),
    ('Khám ngoại tổng quát', 1, 'Khám và chẩn đoán các bệnh về cơ xương khớp, chấn thương, da liễu.', 200000, 70000),
    ('Khám tai - mũi - họng', 1, 'Khám và điều trị các bệnh lý về tai, mũi, họng.', 180000, 60000),
    ('Khám mắt', 1, 'Kiểm tra thị lực, đo khúc xạ và chẩn đoán bệnh về mắt.', 150000, 50000),
    ('Khám răng - hàm - mặt', 1, 'Khám và tư vấn điều trị răng miệng, nha chu, chỉnh nha.', 200000, 70000),
    ('Khám da liễu', 1, 'Chẩn đoán và điều trị các bệnh ngoài da, dị ứng, mụn, viêm da.', 220000, 80000),
    ('Siêu âm ổ bụng', 1, 'Siêu âm kiểm tra các cơ quan trong ổ bụng: gan, thận, tụy, lách, bàng quang.', 250000, 90000),
    ('Xét nghiệm máu tổng quát', 1, 'Xét nghiệm công thức máu, đường huyết, mỡ máu, chức năng gan thận.', 300000, 120000),
    ('Chụp X-quang phổi', 1, 'Chụp X-quang để phát hiện các bệnh lý về phổi và tim.', 200000, 70000);

    """
