"""
Entrypoint to run the FastAPI app from the backend package.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("entrypoint:app", host="0.0.0.0", port=10000)
