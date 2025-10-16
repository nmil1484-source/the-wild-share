import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__ )))

# Get the port from environment variable
port = int(os.environ.get('PORT', 5000))

# Import the Flask app
from src.main import app

# Run the app
if __name__ == '__main__':
    # Try to use gunicorn if available, otherwise use Flask's built-in server
    try:
        from gunicorn.app.base import BaseApplication
        
        class StandaloneApplication(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()
            
            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)
            
            def load(self):
                return self.application
        
        options = {
            'bind': f'0.0.0.0:{port}',
            'workers': 2,
            'timeout': 120,
        }
        
        print(f"Starting gunicorn server on port {port}...")
        StandaloneApplication(app, options).run()
        
    except ImportError:
        # Fallback to Flask's built-in server
        print(f"Gunicorn not available, using Flask development server on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=False)
