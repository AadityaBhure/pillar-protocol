"""
Vercel serverless function entry point
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app
from backend.main import app

# Vercel will use this 'app' variable
