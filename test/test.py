import boto3
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_email_campaign():
    """Run the restaurant email campaign on AWS"""
    
    print("🚀 Running Restaurant Email Campaign")
    print("=" * 50)
    
    # Show email configuration
    email_backend = os.environ.get('EMAIL_BACKEND', 'mock')
    print(f"\n📧 Email Mode: {email_backend.upper()}")
    if email_backend == 'mock':
        print("   ⚠️  Mock mode - emails will be logged only")
    else:
        print(f"   ✅ Real emails will be sent via {email_backend.upper()}")
    print()
    
    # Initialize AWS clients
    ecs = boto3.client('ecs', region_name='us-east-1')
    ec2 = boto3.client('ec2', region_name='us-east-1')
    logs = boto3.client('logs', region_name='us-east-1')
    
    # Get subnet
    subnet_id = ec2.describe_subnets()['Subnets'][0]['SubnetId']
    
    # Run the ECS task
    print("📤 Starting email task on AWS...")
    response = ecs.run_task(
        cluster='restaurant-emails',
        taskDefinition='restaurant-email',
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [subnet_id],
                'assignPublicIp': 'ENABLED'
            }
        }
    )
    
    task_arn = response['tasks'][0]['taskArn']
    task_id = task_arn.split('/')[-1]
    print(f"✅ Task started: {task_id[:12]}...")
    
    # Wait for completion
    print("\n⏳ Processing emails...")
    for i in range(60):  # Max 5 minutes
        task = ecs.describe_tasks(cluster='restaurant-emails', tasks=[task_arn])['tasks'][0]
        status = task['lastStatus']
        
        if status == 'STOPPED':
            print("✅ Task completed!\n")
            break
            
        # Show progress
        print(f"\r⏳ Processing emails... {i*5}s", end='', flush=True)
        time.sleep(5)
    
    # Get and display results
    print("📨 Email Campaign Results:")
    print("-" * 50)
    
    # Wait for logs to be available
    time.sleep(3)
    
    # Try to get logs
    try:
        # Try different log stream formats
        for stream_format in [f'ecs/app/{task_id}', f'ecs/app/{task_id[:8]}']:
            try:
                events = logs.get_log_events(
                    logGroupName='/ecs/restaurant-email',
                    logStreamName=stream_format,
                    startFromHead=True
                )
                
                if events['events']:
                    for event in events['events']:
                        print(event['message'].strip())
                    break
            except:
                continue
                
    except Exception as e:
        print(f"Could not retrieve detailed logs: {e}")
        print("\nCheck CloudWatch for full results:")
        print(f"https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logStream:group=/ecs/restaurant-email")
    
    print("\n" + "=" * 50)
    print("✅ Email campaign complete!")
    
    if email_backend != 'mock':
        print(f"\n📬 Check your inbox for the emails sent via {email_backend.upper()}!")

if __name__ == "__main__":
    try:
        run_email_campaign()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure AWS deployment completed: git push origin main")
        print("2. Check AWS credentials in .env")
        print("3. Verify EMAIL_BACKEND setting in .env")