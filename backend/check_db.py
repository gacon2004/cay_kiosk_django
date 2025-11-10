#!/usr/bin/env python3
"""
Script để kiểm tra cấu trúc database
"""
import os

import django
from django.conf import settings

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection


def check_table_structure():
    """Kiểm tra cấu trúc bảng custom_users"""
    with connection.cursor() as cursor:
        try:
            cursor.execute("DESCRIBE custom_users;")
            columns = cursor.fetchall()

            print("Cấu trúc bảng custom_users:")
            print("-" * 50)
            for col in columns:
                print(f"{col[0]:<20} {col[1]:<15} {col[2]:<5} {col[3]:<5} {col[4]}")
            print("-" * 50)

        except Exception as e:
            print(f"Lỗi khi query database: {e}")


if __name__ == "__main__":
    check_table_structure()
