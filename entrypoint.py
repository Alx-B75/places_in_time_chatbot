"""
Entrypoint to run the FastAPI app from the backend package.
"""


import os, sys

sys.path.insert(0, os.path.dirname(__file__))

from backend.main import app
