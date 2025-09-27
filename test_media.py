#!/usr/bin/env python
"""
Test script to verify media file serving
"""
import os
import requests
from pathlib import Path

# Test if media files exist
media_dir = Path(__file__).parent / "media" / "avatars"
print(f"Media directory: {media_dir}")
print(f"Media directory exists: {media_dir.exists()}")

if media_dir.exists():
    files = list(media_dir.glob("*.png"))
    print(f"PNG files found: {len(files)}")
    for file in files:
        print(f"  - {file.name} ({file.stat().st_size} bytes)")

# Test if Django server is running and serving media files
try:
    response = requests.get("http://127.0.0.1:8000/media/avatars/1048210.png", timeout=5)
    print(f"Django server response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Media files are being served correctly!")
    else:
        print(f"❌ Media files not accessible: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Django server is not running on port 8000")
except Exception as e:
    print(f"❌ Error accessing media files: {e}")
