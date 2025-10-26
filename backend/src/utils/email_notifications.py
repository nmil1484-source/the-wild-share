import os
import boto3
from botocore.exceptions import ClientError

# Initialize AWS SES client
ses_client = boto3.client(
    'ses',
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'thewildshare@gmail.com')
PLATFORM_NAME = "The Wild Share"
PLATFORM_URL = os.environ.get('PLATFORM_URL', 'https://the-wild-share-production.up.railway.app')


def send_email(to_email, subject, html_body, text_body=None):
    """Send an email using AWS SES"""
    try:
        response = ses_client.send_email(
            Source=f"{PLATFORM_NAME} <{SENDER_EMAIL}>",
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'},
                    'Text': {'Data': text_body or html_body, 'Charset': 'UTF-8'}
                }
            }
        )
        print(f"Email sent to {to_email}: {response['MessageId']}")
        return True
    except ClientError as e:
        print(f"Error sending email to {to_email}: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"Unexpected error sending email: {str(e)}")
        return False


def send_booking_confirmation_email(booking, equipment, renter, owner):
    """Send booking confirmation email to renter"""
    subject = f"Booking Confirmed: {equipment.name}"
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #059669;">Booking Confirmed!</h2>
                <p>Hi {renter.first_name},</p>
                <p>Your booking has been confirmed. Here are the details:</p>
                
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #059669;">Booking Details</h3>
                    <p><strong>Equipment:</strong> {equipment.name}</p>
                    <p><strong>Dates:</strong> {booking.start_date} to {booking.end_date}</p>
                    <p><strong>Duration:</strong> {booking.total_days} days</p>
                    <p><strong>Daily Rate:</strong> ${booking.daily_rate:.2f}</p>
                    <p><strong>Total Cost:</strong> ${booking.total_cost:.2f}</p>
                    <p><strong>Security Deposit:</strong> ${booking.deposit_amount:.2f}</p>
                    <p><strong>Booking ID:</strong> #{booking.id}</p>
                </div>
                
                <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #f59e0b;">Owner Contact</h3>
                    <p><strong>Name:</strong> {owner.first_name} {owner.last_name}</p>
                    <p><strong>Email:</strong> {owner.email}</p>
                    {f'<p><strong>Phone:</strong> {owner.phone}</p>' if owner.phone else ''}
                </div>
                
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Contact the owner to arrange pickup details</li>
                    <li>Download and sign the rental agreement</li>
                    <li>Bring valid ID and payment confirmation</li>
                    <li>Inspect equipment before taking possession</li>
                </ol>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="text-align: center;">
                        <a href="{PLATFORM_URL}/api/contracts/rental-agreement/{booking.id}" 
                           style="background-color: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            Download Rental Agreement
                        </a>
                    </p>
                </div>
                
                <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">
                    Questions? Reply to this email or visit <a href="{PLATFORM_URL}">{PLATFORM_NAME}</a>
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email(renter.email, subject, html_body)


def send_new_booking_notification_email(booking, equipment, renter, owner):
    """Send new booking notification to equipment owner"""
    subject = f"New Booking: {equipment.name}"
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #059669;">New Booking Received!</h2>
                <p>Hi {owner.first_name},</p>
                <p>You have a new booking for your equipment:</p>
                
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #059669;">Booking Details</h3>
                    <p><strong>Equipment:</strong> {equipment.name}</p>
                    <p><strong>Dates:</strong> {booking.start_date} to {booking.end_date}</p>
                    <p><strong>Duration:</strong> {booking.total_days} days</p>
                    <p><strong>Your Earnings:</strong> ${booking.total_cost * 0.9:.2f} (after 10% platform fee)</p>
                    <p><strong>Booking ID:</strong> #{booking.id}</p>
                </div>
                
                <div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2563eb;">Renter Information</h3>
                    <p><strong>Name:</strong> {renter.first_name} {renter.last_name}</p>
                    <p><strong>Email:</strong> {renter.email}</p>
                    {f'<p><strong>Phone:</strong> {renter.phone}</p>' if renter.phone else ''}
                    {f'<p><strong>Verified:</strong> ✓ Identity Verified</p>' if renter.is_identity_verified else '<p><strong>Verified:</strong> Not verified</p>'}
                </div>
                
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Contact the renter to arrange pickup details</li>
                    <li>Prepare the equipment for rental</li>
                    <li>Inspect equipment with renter at pickup</li>
                    <li>Have renter sign the rental agreement</li>
                </ol>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="text-align: center;">
                        <a href="{PLATFORM_URL}" 
                           style="background-color: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            View Booking Details
                        </a>
                    </p>
                </div>
                
                <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">
                    Questions? Reply to this email or visit <a href="{PLATFORM_URL}">{PLATFORM_NAME}</a>
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email(owner.email, subject, html_body)


def send_payment_confirmation_email(booking, equipment, renter, payment_amount):
    """Send payment confirmation email to renter"""
    subject = f"Payment Confirmed: {equipment.name}"
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #059669;">Payment Confirmed!</h2>
                <p>Hi {renter.first_name},</p>
                <p>Your payment has been successfully processed.</p>
                
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #059669;">Payment Details</h3>
                    <p><strong>Amount Paid:</strong> ${payment_amount:.2f}</p>
                    <p><strong>Equipment:</strong> {equipment.name}</p>
                    <p><strong>Rental Period:</strong> {booking.start_date} to {booking.end_date}</p>
                    <p><strong>Booking ID:</strong> #{booking.id}</p>
                </div>
                
                <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Security Deposit:</strong> ${booking.deposit_amount:.2f}</p>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #92400e;">
                        Your deposit will be refunded after you return the equipment in good condition.
                    </p>
                </div>
                
                <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">
                    This is your payment receipt. Keep it for your records.
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email(renter.email, subject, html_body)


def send_new_message_notification_email(message, sender, receiver, equipment):
    """Send notification email when user receives a new message"""
    subject = f"New Message from {sender.first_name} about {equipment.name}"
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #059669;">New Message</h2>
                <p>Hi {receiver.first_name},</p>
                <p>You have a new message from {sender.first_name} {sender.last_name}:</p>
                
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>About:</strong> {equipment.name}</p>
                    <p style="margin-top: 15px; padding: 15px; background-color: white; border-left: 4px solid #059669;">
                        {message.message}
                    </p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="text-align: center;">
                        <a href="{PLATFORM_URL}" 
                           style="background-color: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            Reply to Message
                        </a>
                    </p>
                </div>
                
                <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">
                    To manage your notification preferences, visit your <a href="{PLATFORM_URL}">account settings</a>.
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email(receiver.email, subject, html_body)


def send_booking_status_update_email(booking, equipment, renter, new_status):
    """Send email when booking status changes"""
    status_messages = {
        'confirmed': 'Your booking has been confirmed!',
        'active': 'Your rental is now active. Enjoy your adventure!',
        'completed': 'Your rental has been completed. Thank you for using The Wild Share!',
        'cancelled': 'Your booking has been cancelled.'
    }
    
    subject = f"Booking Update: {equipment.name}"
    message = status_messages.get(new_status, f'Your booking status has been updated to: {new_status}')
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #059669;">Booking Status Update</h2>
                <p>Hi {renter.first_name},</p>
                <p>{message}</p>
                
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Equipment:</strong> {equipment.name}</p>
                    <p><strong>Dates:</strong> {booking.start_date} to {booking.end_date}</p>
                    <p><strong>Status:</strong> {new_status.upper()}</p>
                    <p><strong>Booking ID:</strong> #{booking.id}</p>
                </div>
                
                {'''
                <div style="background-color: #dcfce7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Deposit Refund:</strong></p>
                    <p style="margin: 10px 0 0 0; font-size: 14px;">
                        Your security deposit of $''' + f"{booking.deposit_amount:.2f}" + ''' will be refunded within 2-3 business days.
                    </p>
                </div>
                ''' if new_status == 'completed' else ''}
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="text-align: center;">
                        <a href="{PLATFORM_URL}" 
                           style="background-color: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            View Booking Details
                        </a>
                    </p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_email(renter.email, subject, html_body)

