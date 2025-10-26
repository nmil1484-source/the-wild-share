from flask import Blueprint, send_file
from datetime import datetime, timedelta
import os

sample_contract_bp = Blueprint('sample_contract', __name__)

@sample_contract_bp.route('/sample-contract', methods=['GET'])
def get_sample_contract():
    """Serve the sample contract HTML for preview"""
    
    # Sample data
    template_data = {
        'booking_date': datetime.now().strftime('%B %d, %Y'),
        'owner_name': 'John Smith',
        'owner_email': 'john.smith@email.com',
        'owner_phone': '(555) 123-4567',
        'owner_address': '123 Mountain View Dr, Denver, CO 80202',
        'renter_name': 'Sarah Johnson',
        'renter_email': 'sarah.j@email.com',
        'renter_phone': '(555) 987-6543',
        'renter_address': '456 Lake Street, Boulder, CO 80301',
        'equipment_name': 'REI Co-op Flash 2-Person Tent',
        'equipment_category': 'Camping Gear',
        'equipment_description': '2-person backpacking tent, lightweight, includes rainfly and footprint',
        'booking_id': 'WS-2024-001234',
        'start_date': (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y'),
        'end_date': (datetime.now() + timedelta(days=10)).strftime('%B %d, %Y'),
        'rental_days': '3',
        'daily_price': '25.00',
        'subtotal': '75.00',
        'platform_fee': '7.50',
        'total_cost': '82.50',
        'deposit_amount': '41.25',
        'total_charged': '123.75',
        'payment_date': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'pickup_location': '123 Mountain View Dr, Denver, CO 80202',
        'pickup_datetime': (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y at 10:00 AM'),
        'return_location': '123 Mountain View Dr, Denver, CO 80202',
        'return_datetime': (datetime.now() + timedelta(days=10)).strftime('%B %d, %Y by 6:00 PM'),
    }
    
    # Read template
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'contract_templates', 'rental_agreement_v2.html')
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Replace placeholders
    for key, value in template_data.items():
        template = template.replace('{{' + key + '}}', str(value))
    
    # Return HTML
    from flask import Response
    return Response(template, mimetype='text/html')

