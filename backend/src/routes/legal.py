from flask import Blueprint, send_from_directory
import os

legal_bp = Blueprint('legal', __name__)

# Get the absolute path to the contract templates directory
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'contract_templates')

@legal_bp.route('/terms-of-service')
def terms_of_service():
    return send_from_directory(TEMPLATE_DIR, 'terms_of_service.html')

@legal_bp.route('/privacy-policy')
def privacy_policy():
    return send_from_directory(TEMPLATE_DIR, 'privacy_policy.html')

