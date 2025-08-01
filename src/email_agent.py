"""
Restaurant Email Agent using Amazon Bedrock AgentCore
Handles email sending with multiple backends (mock, SES, SMTP)
"""
import os
import json
import boto3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import tool

# Create the AgentCore app
app = BedrockAgentCoreApp("restaurant-email-agent")

# Email configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'mock')  # mock, ses, smtp
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@restaurant.com')

# Initialize AWS clients
ses_client = boto3.client('ses', region_name='us-east-1') if EMAIL_BACKEND == 'ses' else None

@tool
async def send_restaurant_email(
    to_email: str,
    customer_name: str,
    subject: str,
    body: str
) -> Dict[str, Any]:
    """
    Send email to restaurant customer using configured backend
    
    Args:
        to_email: Customer email address
        customer_name: Customer's full name
        subject: Email subject line
        body: Email body content
    
    Returns:
        Dict with success status and details
    """
    
    if EMAIL_BACKEND == 'mock':
        # Mock mode - just log the email
        print(f"\n[MOCK EMAIL MODE]")
        print(f"To: {customer_name} <{to_email}>")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("-" * 50)
        
        return {
            'success': True,
            'backend': 'mock',
            'message': f'Email logged for {customer_name} (not sent)',
            'details': 'Using mock mode - switch EMAIL_BACKEND to ses or smtp for real emails'
        }
    
    elif EMAIL_BACKEND == 'ses':
        # AWS SES mode - send real email
        try:
            response = ses_client.send_email(
                Source=SENDER_EMAIL,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )
            
            print(f"✅ Email sent via SES to {customer_name}")
            
            return {
                'success': True,
                'backend': 'ses',
                'message': f'Email sent to {customer_name}',
                'message_id': response['MessageId']
            }
            
        except Exception as e:
            print(f"❌ SES Error: {str(e)}")
            
            # Check if it's a verification error
            if 'MessageRejected' in str(e) and 'not verified' in str(e):
                return {
                    'success': False,
                    'backend': 'ses',
                    'error': 'Email address not verified in SES',
                    'fix': f'Run: aws ses verify-email-identity --email-address {SENDER_EMAIL}'
                }
            
            return {
                'success': False,
                'backend': 'ses',
                'error': str(e)
            }
    
    elif EMAIL_BACKEND == 'smtp':
        # SMTP mode (Gmail, etc)
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_password = os.environ.get('SMTP_PASSWORD', '')
        
        if not smtp_password:
            return {
                'success': False,
                'backend': 'smtp',
                'error': 'SMTP_PASSWORD not set',
                'fix': 'Add SMTP_PASSWORD to your environment variables'
            }
        
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(SENDER_EMAIL, smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent via SMTP to {customer_name}")
            
            return {
                'success': True,
                'backend': 'smtp',
                'message': f'Email sent to {customer_name}'
            }
            
        except Exception as e:
            print(f"❌ SMTP Error: {str(e)}")
            return {
                'success': False,
                'backend': 'smtp',
                'error': str(e)
            }
    
    else:
        return {
            'success': False,
            'error': f'Unknown email backend: {EMAIL_BACKEND}'
        }

@tool
async def get_email_status() -> Dict[str, Any]:
    """Get current email configuration and status"""
    
    status = {
        'backend': EMAIL_BACKEND,
        'sender_email': SENDER_EMAIL,
        'ready': True
    }
    
    if EMAIL_BACKEND == 'ses':
        try:
            # Check SES sending quota
            quota = ses_client.get_send_quota()
            status['ses_quota'] = {
                'max_24_hour': quota['Max24HourSend'],
                'sent_last_24_hours': quota['SentLast24Hours'],
                'max_send_rate': quota['MaxSendRate']
            }
            
            # Check if sender is verified
            identities = ses_client.list_verified_email_addresses()
            status['sender_verified'] = SENDER_EMAIL in identities['VerifiedEmailAddresses']
            
            if not status['sender_verified']:
                status['ready'] = False
                status['fix'] = f'Verify sender: aws ses verify-email-identity --email-address {SENDER_EMAIL}'
                
        except Exception as e:
            status['error'] = str(e)
            status['ready'] = False
    
    elif EMAIL_BACKEND == 'smtp':
        status['smtp_configured'] = bool(os.environ.get('SMTP_PASSWORD'))
        if not status['smtp_configured']:
            status['ready'] = False
            status['fix'] = 'Set SMTP_PASSWORD environment variable'
    
    return status

# Entry point for the agent
@app.handler
async def handle_email_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Main handler for email requests"""
    
    action = event.get('action', 'send_email')
    
    if action == 'send_email':
        return await send_restaurant_email(
            to_email=event['to_email'],
            customer_name=event['customer_name'],
            subject=event['subject'],
            body=event['body']
        )
    elif action == 'get_status':
        return await get_email_status()
    else:
        return {'error': f'Unknown action: {action}'}

if __name__ == "__main__":
    # For local testing
    import asyncio
    
    # Test status check
    print("Checking email configuration...")
    status = asyncio.run(get_email_status())
    print(json.dumps(status, indent=2))
    
    # Test sending
    if status['ready']:
        print("\nTesting email send...")
        result = asyncio.run(send_restaurant_email(
            to_email="test@example.com",
            customer_name="Test User",
            subject="Test Email",
            body="This is a test email from the restaurant system."
        ))
        print(json.dumps(result, indent=2))