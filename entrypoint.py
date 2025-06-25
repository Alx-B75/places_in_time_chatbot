"""
Entrypoint to run the FastAPI app from the backend package.
"""


# In /opt/render/project/src/entrypoint.py
import os
import sys
import uvicorn

project_root_dir = os.path.dirname(os.path.abspath(__file__))
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

# Import the app (this will now work as project_root_dir is in sys.path)
from backend.main import app

# Explicitly run uvicorn
if __name__ == "__main__":
    # Using the 'app' object imported above
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))