import boto3
import json
import os
from typing import Dict, Any

def read_customers_from_s3():
    """Read customer data from S3"""
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket='aiawsattack-bucket',
        Key='customers.json'
    )
    return json.loads(response['Body'].read())

def send_email(to_email: str, subject: str, body: str, customer_name: str) -> str:
    """
    Send email using configured backend
    
    Backends:
    - mock: Log emails for testing (default)
    - ses: Send via AWS SES
    - smtp: Send via SMTP (Gmail, etc)
    - agentcore: Use deployed Bedrock agent
    """
    
    email_backend = os.environ.get('EMAIL_BACKEND', 'mock')
    
    if email_backend == 'agentcore':
        # Use the deployed AgentCore email agent
        bedrock_agent = boto3.client('bedrock-agent-runtime')
        
        try:
            # Invoke the email agent
            response = bedrock_agent.invoke_inline_agent(
                inputText=f"Send email to {customer_name}",
                agentResourceRoleArn=os.environ.get('AGENT_ROLE_ARN'),
                foundationModel='anthropic.claude-3-haiku-20240307-v1:0',
                instruction='You are an email sending agent.',
                actionGroups=[{
                    'actionGroupName': 'EmailActions',
                    'parentActionGroupSignature': 'AMAZON.UserInput',
                    'actionGroupExecutor': {
                        'lambda': os.environ.get('EMAIL_AGENT_FUNCTION_ARN')
                    }
                }],
                sessionState={
                    'invocationId': '1',
                    'returnControlInvocationResults': [{
                        'functionResult': {
                            'actionGroup': 'EmailActions',
                            'action': 'send_email',
                            'function': 'send_restaurant_email',
                            'responseBody': {
                                'TEXT': {
                                    'body': json.dumps({
                                        'to_email': to_email,
                                        'customer_name': customer_name,
                                        'subject': subject,
                                        'body': body
                                    })
                                }
                            }
                        }
                    }]
                }
            )
            
            # Extract result from response
            result = json.loads(response['completion'])
            if result.get('success'):
                return f"Email sent to {customer_name} via AgentCore"
            else:
                return f"Failed to send email: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            print(f"AgentCore error: {str(e)}")
            print("Falling back to local email handling...")
            email_backend = 'mock'  # Fall back to mock
    
    # Direct implementation (mock, ses, or smtp)
    if email_backend == 'mock':
        print(f"\n--- EMAIL TO: {customer_name} ({to_email}) ---")
        print(f"SUBJECT: {subject}")
        print(f"BODY:\n{body}")
        print("--- END EMAIL ---\n")
        return f"Email sent to {customer_name}"
    
    elif email_backend == 'ses':
        ses = boto3.client('ses', region_name='us-east-1')
        sender_email = os.environ.get('SENDER_EMAIL', 'noreply@restaurant.com')
        
        try:
            response = ses.send_email(
                Source=sender_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )
            print(f"✅ Email sent via SES to {customer_name}")
            return f"Email sent to {customer_name} - ID: {response['MessageId']}"
        except Exception as e:
            print(f"❌ SES Error: {str(e)}")
            if 'MessageRejected' in str(e) and 'not verified' in str(e):
                print(f"Fix: aws ses verify-email-identity --email-address {sender_email}")
            return f"Failed to send email: {str(e)}"
    
    elif email_backend == 'smtp':
        # SMTP implementation
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        sender_email = os.environ.get('SENDER_EMAIL', 'noreply@restaurant.com')
        sender_password = os.environ.get('SMTP_PASSWORD')
        
        if not sender_password:
            print("⚠️  SMTP password not set, using mock mode")
            print(f"\n--- EMAIL TO: {customer_name} ({to_email}) ---")
            print(f"SUBJECT: {subject}")
            print(f"BODY:\n{body}")
            print("--- END EMAIL ---\n")
            return f"Email logged for {customer_name} (SMTP not configured)"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            print(f"✅ Email sent via SMTP to {customer_name}")
            return f"Email sent to {customer_name} via SMTP"
            
        except Exception as e:
            print(f"❌ SMTP Error: {str(e)}")
            return f"SMTP error: {str(e)}"
    
    else:
        return f"Unknown email backend: {email_backend}"