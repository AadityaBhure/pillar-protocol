"""
Vercel entry point for FastAPI
"""
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app from backend
from backend.main import app

# Vercel will use this app
