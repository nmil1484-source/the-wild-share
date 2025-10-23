import os
import sys
# Add parent directory to path so src module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize extensions
jwt = JWTManager(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

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
    try:
        db.create_all()
        print("Database tables ready!")
    except Exception as e:
        print(f"Database initialization note: {e}")
        print("Tables may already exist, continuing...")
    
    # Add location column to equipment table if it doesn't exist
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            # Check if location column exists
            result = conn.execute(text("PRAGMA table_info(equipment)"))
            columns = [row[1] for row in result]
            if 'location' not in columns:
                conn.execute(text("ALTER TABLE equipment ADD COLUMN location VARCHAR(255)"))
                conn.commit()
                print("Added location column to equipment table")
    except Exception as e:
        print(f"Migration note: {e}")

# Register API blueprints FIRST (so they take priority)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
# Apply rate limiting to auth endpoints
# Note: Rate limiting is configured but not applied to specific endpoints to avoid startup errors
# limiter.limit("5 per hour")(auth_bp.view_functions['register'])
# limiter.limit("10 per minute")(auth_bp.view_functions['login'])
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
    return send_from_directory(os.path.join(app.static_folder, 'assets'), path)

# Serve uploaded images
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    uploads_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    return send_from_directory(uploads_folder, filename)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "The Wild Share API is running"})

# Serve frontend - this MUST be last
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # If path is empty or doesn't exist, serve index.html
    if path == '':
        return send_from_directory(app.static_folder, 'index.html')
    
    # Check if the file exists in static folder
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    
    # For all other routes (React Router), serve index.html
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# Force rebuild Thu Oct 23 16:42:10 EDT 2025
