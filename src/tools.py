import boto3
import json

def read_customers_from_s3():
    """Read customer data from S3"""
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket='aiawsattack-bucket',
        Key='customers.json'
    )
    return json.loads(response['Body'].read())

def send_email(to_email: str, subject: str, body: str, customer_name: str) -> str:
    """Mock email sender - just logs for now"""
    print(f"\n--- EMAIL TO: {customer_name} ({to_email}) ---")
    print(f"SUBJECT: {subject}")
    print(f"BODY:\n{body}")
    print("--- END EMAIL ---\n")
    return f"Email sent to {customer_name}"