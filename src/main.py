import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from datetime import timedelta

from src.models.user import db
from src.models.equipment import Equipment
from src.models.booking import Booking
from src.models.payment import Payment
from src.models.message import Message

from src.routes.auth import auth_bp
from src.routes.equipment import equipment_bp
from src.routes.bookings import bookings_bp
from src.routes.payments import payments_bp
from src.routes.stripe_connect import stripe_connect_bp
from src.routes.messages import messages_bp
from src.routes.upload import upload_bp
from src.routes.verification import verification_bp

# Get the absolute path to the static folder
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
print(f"Static folder path: {STATIC_FOLDER}")
print(f"Static folder exists: {os.path.exists(STATIC_FOLDER)}")

app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize extensions
jwt = JWTManager(app)

# Database configuration
# Use PostgreSQL from Railway or fallback to SQLite for local development
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Railway PostgreSQL - convert postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local development fallback to SQLite
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables ready!")

# Register API blueprints FIRST (so they take priority)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(equipment_bp, url_prefix='/api')
app.register_blueprint(bookings_bp, url_prefix='/api')
app.register_blueprint(payments_bp, url_prefix='/api')
app.register_blueprint(stripe_connect_bp, url_prefix='/api/stripe')
app.register_blueprint(messages_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(verification_bp, url_prefix='/api')

# Serve static assets (CSS, JS, images)
@app.route('/assets/<path:path>')
def serve_assets(path):
    assets_folder = os.path.join(STATIC_FOLDER, 'assets')
    print(f"Serving asset: {path} from {assets_folder}")
    return send_from_directory(assets_folder, path)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "The Wild Share API is running"})

# Serve frontend - this MUST be last
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    print(f"Requested path: {path}")
    print(f"Static folder: {STATIC_FOLDER}")
    
    # If path is empty or is the root, serve index.html
    if path == '' or path == '/':
        index_path = os.path.join(STATIC_FOLDER, 'index.html')
        print(f"Serving index.html from: {index_path}")
        print(f"Index.html exists: {os.path.exists(index_path)}")
        return send_from_directory(STATIC_FOLDER, 'index.html')
    
    # Check if the file exists in static folder
    file_path = os.path.join(STATIC_FOLDER, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        print(f"Serving file: {file_path}")
        return send_from_directory(STATIC_FOLDER, path)
    
    # For all other routes (React Router), serve index.html
    print(f"Path not found, serving index.html for: {path}")
    return send_from_directory(STATIC_FOLDER, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

