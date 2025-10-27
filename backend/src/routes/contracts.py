from flask import Blueprint, send_file, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import os
from io import BytesIO
from weasyprint import HTML
from ..models.booking import Booking, db
from ..models.equipment import Equipment
from ..models.user import User

contracts_bp = Blueprint('contracts', __name__)

# Get the absolute path to the contract templates directory
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'contract_templates')

def render_contract_template(template_name, data):
    """
    Render a contract template with the provided data
    """
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Replace all template variables
    for key, value in data.items():
        template_content = template_content.replace(f'{{{{{key}}}}}', str(value))
    
    return template_content

@contracts_bp.route('/api/contracts/rental-agreement/<int:booking_id>')
@login_required
def download_rental_agreement(booking_id):
    """
    Generate and download the rental agreement for a booking
    """
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify the user is either the renter or the owner
    if current_user.id != booking.renter_id and current_user.id != booking.equipment.owner_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get related data
    equipment = booking.equipment
    owner = User.query.get(equipment.owner_id)
    renter = User.query.get(booking.renter_id)
    
    # Calculate rental details
    rental_days = (booking.end_date - booking.start_date).days
    if rental_days == 0:
        rental_days = 1  # Minimum 1 day
    
    total_cost = equipment.daily_price * rental_days
    deposit_amount = total_cost * 0.5  # 50% deposit
    total_paid = total_cost + deposit_amount
    
    # Prepare template data
    platform_fee = total_cost * 0.10  # 10% platform fee
    data = {
        'booking_date': datetime.now().strftime('%B %d, %Y'),
        'owner_name': owner.name,
        'owner_email': owner.email,
        'owner_phone': owner.phone or 'Not provided',
        'owner_address': 'Address on file',
        'renter_name': renter.name,
        'renter_email': renter.email,
        'renter_phone': renter.phone or 'Not provided',
        'renter_address': 'Address on file',
        'equipment_name': equipment.name,
        'equipment_category': equipment.category,
        'equipment_description': equipment.specifications or 'See equipment listing',
        'start_date': booking.start_date.strftime('%B %d, %Y'),
        'end_date': booking.end_date.strftime('%B %d, %Y'),
        'rental_days': rental_days,
        'daily_price': f'{equipment.daily_price:.2f}',
        'subtotal': f'{total_cost:.2f}',
        'platform_fee': f'{platform_fee:.2f}',
        'total_cost': f'{total_cost + platform_fee:.2f}',
        'deposit_amount': f'{deposit_amount:.2f}',
        'total_charged': f'{total_paid + platform_fee:.2f}',
        'booking_id': booking.id,
        'payment_date': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'pickup_location': equipment.location or 'See equipment listing',
        'pickup_datetime': booking.start_date.strftime('%B %d, %Y at 10:00 AM'),
        'return_location': equipment.location or 'See equipment listing',
        'return_datetime': booking.end_date.strftime('%B %d, %Y by 6:00 PM')
    }
    
    # Render the template
    html_content = render_contract_template('rental_agreement_short.html', data)
    
    # Convert to PDF
    pdf = HTML(string=html_content).write_pdf()
    
    # Create a BytesIO object to send the PDF
    pdf_io = BytesIO(pdf)
    pdf_io.seek(0)
    
    # Generate filename
    filename = f'Rental_Agreement_{booking.id}_{equipment.name.replace(" ", "_")}.pdf'
    
    return send_file(
        pdf_io,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@contracts_bp.route('/api/contracts/liability-waiver/<int:booking_id>')
@login_required
def download_liability_waiver(booking_id):
    """
    Generate and download the liability waiver for a booking
    """
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify the user is either the renter or the owner
    if current_user.id != booking.renter_id and current_user.id != booking.equipment.owner_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get related data
    equipment = booking.equipment
    owner = User.query.get(equipment.owner_id)
    renter = User.query.get(booking.renter_id)
    
    # Prepare template data
    data = {
        'renter_name': renter.name,
        'renter_email': renter.email,
        'renter_phone': renter.phone or 'Not provided',
        'owner_name': owner.name,
        'equipment_name': equipment.name,
        'start_date': booking.start_date.strftime('%B %d, %Y'),
        'end_date': booking.end_date.strftime('%B %d, %Y'),
        'booking_id': booking.id,
        'generated_date': datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }
    
    # Note: The short template includes both rental agreement and liability waiver
    # So we'll use the same template but with different data focus
    html_content = render_contract_template('rental_agreement_short.html', data)
    
    # Convert to PDF
    pdf = HTML(string=html_content).write_pdf()
    
    # Create a BytesIO object to send the PDF
    pdf_io = BytesIO(pdf)
    pdf_io.seek(0)
    
    # Generate filename
    filename = f'Liability_Waiver_{booking.id}_{equipment.name.replace(" ", "_")}.pdf'
    
    return send_file(
        pdf_io,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@contracts_bp.route('/api/contracts/all/<int:booking_id>')
@login_required
def download_all_contracts(booking_id):
    """
    Generate and download all contracts as a ZIP file
    """
    from zipfile import ZipFile
    
    # Get the booking
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify the user is either the renter or the owner
    if current_user.id != booking.renter_id and current_user.id != booking.equipment.owner_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get related data
    equipment = booking.equipment
    owner = User.query.get(equipment.owner_id)
    renter = User.query.get(booking.renter_id)
    
    # Calculate rental details
    rental_days = (booking.end_date - booking.start_date).days
    if rental_days == 0:
        rental_days = 1
    
    total_cost = equipment.daily_price * rental_days
    deposit_amount = total_cost * 0.5
    total_paid = total_cost + deposit_amount
    
    # Prepare data for rental agreement
    rental_data = {
        'rental_date': datetime.now().strftime('%B %d, %Y'),
        'owner_name': owner.name,
        'owner_email': owner.email,
        'owner_phone': owner.phone or 'Not provided',
        'renter_name': renter.name,
        'renter_email': renter.email,
        'renter_phone': renter.phone or 'Not provided',
        'equipment_name': equipment.name,
        'equipment_category': equipment.category,
        'equipment_specs': equipment.specifications or 'See equipment listing',
        'start_date': booking.start_date.strftime('%B %d, %Y'),
        'end_date': booking.end_date.strftime('%B %d, %Y'),
        'rental_days': rental_days,
        'daily_rate': f'{equipment.daily_price:.2f}',
        'total_cost': f'{total_cost:.2f}',
        'deposit_amount': f'{deposit_amount:.2f}',
        'total_paid': f'{total_paid:.2f}',
        'booking_id': booking.id,
        'generated_date': datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }
    
    # Prepare data for liability waiver
    waiver_data = {
        'renter_name': renter.name,
        'renter_email': renter.email,
        'renter_phone': renter.phone or 'Not provided',
        'owner_name': owner.name,
        'equipment_name': equipment.name,
        'start_date': booking.start_date.strftime('%B %d, %Y'),
        'end_date': booking.end_date.strftime('%B %d, %Y'),
        'booking_id': booking.id,
        'generated_date': datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }
    
    # Generate PDF (short template includes both agreement and waiver)
    rental_html = render_contract_template('rental_agreement_short.html', rental_data)
    rental_pdf = HTML(string=rental_html).write_pdf()
    
    # Create ZIP file (short template includes both agreement and waiver in one PDF)
    zip_io = BytesIO()
    with ZipFile(zip_io, 'w') as zip_file:
        zip_file.writestr(f'Rental_Contract_{booking.id}.pdf', rental_pdf)
    
    zip_io.seek(0)
    
    # Generate filename
    filename = f'Rental_Contracts_{booking.id}_{equipment.name.replace(" ", "_")}.zip'
    
    return send_file(
        zip_io,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )

