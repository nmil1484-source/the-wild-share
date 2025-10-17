import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from datetime import timedelta

from src.models.user import db
from src.models.equipment import Equipment
from src.models.booking import Booking
from src.models.payment import Payment

from src.routes.auth import auth_bp
from src.routes.equipment import equipment_bp
from src.routes.bookings import bookings_bp
from src.routes.payments import payments_bp
from src.routes.stripe_connect import stripe_connect_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize extensions
jwt = JWTManager(app)


# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(equipment_bp, url_prefix='/api')
app.register_blueprint(bookings_bp, url_prefix='/api')
app.register_blueprint(payments_bp, url_prefix='/api')
app.register_blueprint(stripe_connect_bp, url_prefix='/api/stripe')

# Database configuration
# Use /tmp directory for Railway deployment (writable)
db_path = os.environ.get('DATABASE_PATH', '/tmp/app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

# Test route to verify Flask is working
@app.route('/test')
def test():
    static_path = app.static_folder
    if static_path and os.path.exists(static_path):
        files = os.listdir(static_path)
        return f"Static folder exists at: {static_path}<br>Files: {files}"
    else:
        return f"Static folder not found. Looking for: {static_path}"

# Serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return f"index.html not found at: {index_path}", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

