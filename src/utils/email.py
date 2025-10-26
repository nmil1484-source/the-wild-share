import os
import boto3
from botocore.exceptions import ClientError

def send_password_reset_email(to_email, reset_link):
    """
    Send a password reset email using AWS SES
    
    Args:
        to_email (str): Recipient email address
        reset_link (str): Password reset link URL
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # AWS SES configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-2')
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'thewildshare@gmail.com')
    
    print(f"[EMAIL DEBUG] Attempting to send email to: {to_email}")
    print(f"[EMAIL DEBUG] From: {SENDER_EMAIL}")
    print(f"[EMAIL DEBUG] Region: {AWS_REGION}")
    print(f"[EMAIL DEBUG] AWS Access Key ID exists: {bool(os.environ.get('AWS_ACCESS_KEY_ID'))}")
    print(f"[EMAIL DEBUG] AWS Secret Key exists: {bool(os.environ.get('AWS_SECRET_ACCESS_KEY'))}")
    
    # Create SES client
    ses_client = boto3.client(
        'ses',
        region_name=AWS_REGION,
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    
    # Email subject and body
    SUBJECT = "Reset Your Password - The Wild Share"
    
    # HTML email body
    BODY_HTML = f"""
    <html>
    <head></head>
    <body>
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c5f2d;">Reset Your Password</h2>
        <p>Hi there,</p>
        <p>You requested to reset your password for The Wild Share. Click the button below to set a new password:</p>
        <div style="text-align: center; margin: 30px 0;">
          <a href="{reset_link}" 
             style="background-color: #2c5f2d; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
            Reset Password
          </a>
        </div>
        <p>Or copy and paste this link into your browser:</p>
        <p style="color: #666; word-break: break-all;">{reset_link}</p>
        <p style="color: #999; font-size: 14px; margin-top: 30px;">
          This link will expire in 15 minutes for security reasons.
        </p>
        <p style="color: #999; font-size: 14px;">
          If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="color: #999; font-size: 12px;">
          Best regards,<br>
          The Wild Share Team<br>
          <a href="https://www.thewildshare.com" style="color: #2c5f2d;">www.thewildshare.com</a>
        </p>
      </div>
    </body>
    </html>
    """
    
    # Plain text email body (fallback)
    BODY_TEXT = f"""
    Reset Your Password - The Wild Share
    
    Hi there,
    
    You requested to reset your password for The Wild Share. Click the link below to set a new password:
    
    {reset_link}
    
    This link will expire in 15 minutes for security reasons.
    
    If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
    
    Best regards,
    The Wild Share Team
    www.thewildshare.com
    """
    
    # Character encoding
    CHARSET = "UTF-8"
    
    try:
        # Send the email
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [to_email],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER_EMAIL,
        )
        
        print(f"[EMAIL SUCCESS] Email sent successfully! Message ID: {response['MessageId']}")
        print(f"[EMAIL SUCCESS] Sent to: {to_email}")
        return True
        
    except ClientError as e:
        print(f"[EMAIL ERROR] ClientError sending email: {e.response['Error']['Message']}")
        print(f"[EMAIL ERROR] Error Code: {e.response['Error']['Code']}")
        print(f"[EMAIL ERROR] Full response: {e.response}")
        return False
    except Exception as e:
        print(f"[EMAIL ERROR] Unexpected error sending email: {str(e)}")
        print(f"[EMAIL ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[EMAIL ERROR] Traceback: {traceback.format_exc()}")
        return False

