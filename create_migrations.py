#!/usr/bin/env python
"""
Script to create migrations for CloudinaryField changes
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    print("🔄 Creating migrations for CloudinaryField changes...")
    
    # Create migrations for all apps
    apps = ['accounts', 'social', 'dm']
    
    for app in apps:
        print(f"📝 Creating migration for {app}...")
        execute_from_command_line(['manage.py', 'makemigrations', app])
    
    print("✅ Migrations created successfully!")
    print("📋 Next steps:")
    print("1. Run: python manage.py migrate")
    print("2. Deploy to Railway")
    print("3. Test new uploads - they should go to Cloudinary!")
