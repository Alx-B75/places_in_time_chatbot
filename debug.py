"""
Debug script to print current working directory and sys.path for Render deployment.
"""

import os
import sys

print("🛠 Current working directory:", os.getcwd())
print("🛠 Python sys.path:")
for path in sys.path:
    print("   -", path)

print("🛠 Contents of CWD:")
for f in os.listdir():
    print("   •", f)

# Try importing backend.main explicitly
try:
    from backend.main import app
    print("✅ Successfully imported backend.main")
except ModuleNotFoundError as e:
    print("❌ ModuleNotFoundError:", e)
except Exception as e:
    print("❌ Other import error:", e)
