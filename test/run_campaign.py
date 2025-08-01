import boto3
import time
import json
from datetime import datetime
import os

# Load .env file if it exists
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

def main():
    print("🚀 Restaurant Email Campaign Runner")
    print("=" * 50)
    
    # Initialize AWS clients
    s3 = boto3.client('s3', region_name='us-east-1')
    ecs = boto3.client('ecs', region_name='us-east-1')
    ec2 = boto3.client('ec2', region_name='us-east-1')
    logs = boto3.client('logs', region_name='us-east-1')
    
    # 1. Check if customer data exists
    print("\n📋 Checking customer data in S3...")
    try:
        s3.head_object(Bucket='aiawsattack-bucket', Key='customers.json')
        print("✅ Customer data found")
    except:
        print("❌ Customer data not found. Run deployment first!")
        return
    
    # 2. Get subnet for task
    print("\n🌐 Getting network configuration...")
    subnets = ec2.describe_subnets()
    subnet_id = subnets['Subnets'][0]['SubnetId']
    print(f"✅ Using subnet: {subnet_id}")
    
    # 3. Run the ECS task
    print("\n📧 Starting email campaign task...")
    try:
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
        print(f"✅ Task started: {task_id}")
    except Exception as e:
        print(f"❌ Failed to start task: {e}")
        print("Make sure the deployment completed successfully.")
        return
    
    # 4. Wait for task to complete
    print("\n⏳ Waiting for task to complete...")
    waiter = ecs.get_waiter('tasks_stopped')
    try:
        waiter.wait(
            cluster='restaurant-emails',
            tasks=[task_arn],
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 60  # 5 minutes max
            }
        )
        print("✅ Task completed!")
    except Exception as e:
        print(f"⚠️ Task wait timeout: {e}")
    
    # 5. Check task status
    task_detail = ecs.describe_tasks(
        cluster='restaurant-emails',
        tasks=[task_arn]
    )
    
    task = task_detail['tasks'][0]
    print(f"   Final status: {task['lastStatus']}")
    if 'stoppedReason' in task:
        print(f"   Stop reason: {task['stoppedReason']}")
    
    # 6. Get the results from CloudWatch Logs
    print("\n📨 Email Campaign Results:")
    print("-" * 50)
    
    # Wait a bit for logs to propagate
    time.sleep(5)
    
    # Try different log stream name formats
    log_stream_names = [
        f'ecs/app/{task_id}',
        f'ecs/app/{task_id[:8]}',
        f'ecs/app/{task_id.split("-")[0]}'
    ]
    
    log_events = []
    for stream_name in log_stream_names:
        try:
            response = logs.get_log_events(
                logGroupName='/ecs/restaurant-email',
                logStreamName=stream_name,
                startFromHead=True
            )
            log_events = response['events']
            if log_events:
                break
        except:
            continue
    
    if log_events:
        for event in log_events:
            print(event['message'].strip())
    else:
        print("No logs found. This might mean:")
        print("- The task is still initializing")
        print("- The log group doesn't exist")
        print("- The task failed to start")
        
        # List available log streams to help debug
        try:
            streams = logs.describe_log_streams(
                logGroupName='/ecs/restaurant-email',
                orderBy='LastEventTime',
                descending=True,
                limit=5
            )
            if streams['logStreams']:
                print("\nAvailable log streams:")
                for stream in streams['logStreams']:
                    print(f"  - {stream['logStreamName']}")
        except:
            pass
    
    print("\n✅ Campaign run complete!")
    print(f"   Task ARN: {task_arn}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()