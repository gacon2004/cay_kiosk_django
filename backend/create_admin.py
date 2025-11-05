import django
import os

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
