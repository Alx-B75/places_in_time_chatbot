"""
Entrypoint to run the FastAPI app from the backend package.
"""

import os
import sys
import uvicorn

# Get the absolute path to the directory containing this entrypoint.py file.
# This will be /opt/render/project/src/ (your project root).
project_root_dir = os.path.dirname(os.path.abspath(__file__))

# Add the project root directory to Python's module search path (sys.path).
# This makes 'backend' (your backend folder) discoverable as a top-level package.
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

# Now, Python can find 'backend.main' because project_root_dir is in sys.path.
# This line will successfully import your FastAPI app.
from backend.main import app

# Explicitly run Uvicorn using the imported 'app' object.
# The port is retrieved from the environment variable provided by Render.
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Default to 10000 if PORT env var is not set
    uvicorn.run(app, host="0.0.0.0", port=port)
