#!/usr/bin/env python3
"""
WSGI entry point for The Wild Share application
"""
import os
import sys

# Add the current directory to Python path so 'src' module can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import the app from src.main
from src.main import app

if __name__ == "__main__":
    app.run()

