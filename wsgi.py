import os
import sys

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from src.main import app

if __name__ == "__main__":
    app.run()

