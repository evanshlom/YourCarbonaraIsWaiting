import boto3
import json
import time
import sys
import os
from pathlib import Path

# Load .env if exists
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

def test_crew_deployment():
    # Explicitly set AWS credentials for boto3
    ecs = boto3.client(
        'ecs', 
        region_name='us-east-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    ec2 = boto3.client(
        'ec2', 
        region_name='us-east-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    logs = boto3.client(
        'logs', 
        region_name='us-east-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    # Get subnet
    subnet_id = ec2.describe_subnets()['Subnets'][0]['SubnetId']
    
    # Get topic from env or use default
    topic = os.getenv('CREW_TEST_TOPIC', 'I want to create rugpull reaction videos. Focus on crypto, poopcoins, and nfts.')
    
    # Run task
    print("Starting CrewAI task...")
    response = ecs.run_task(
        cluster='crewai',
        taskDefinition='content-crew',
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [subnet_id],
                'assignPublicIp': 'ENABLED'
            }
        },
        overrides={
            'containerOverrides': [{
                'name': 'crew',
                'environment': [{
                    'name': 'TOPIC',
                    'value': topic
                }]
            }]
        }
    )
    
    task_arn = response['tasks'][0]['taskArn']
    print(f"Task started: {task_arn}")
    
    # Wait for completion
    print("Waiting for task to complete...")
    waiter = ecs.get_waiter('tasks_stopped')
    waiter.wait(cluster='crewai', tasks=[task_arn])
    
    # Check task status
    task_details = ecs.describe_tasks(cluster='crewai', tasks=[task_arn])
    task = task_details['tasks'][0]
    print(f"Task status: {task['lastStatus']}")
    print(f"Stop reason: {task.get('stoppedReason', 'N/A')}")
    
    # Get logs
    print("Fetching results...")
    
    # Try different log stream patterns
    task_id = task_arn.split('/')[-1]
    possible_streams = [
        f"ecs/crew/{task_id}",
        f"content-crew/crew/{task_id}",
        f"crew/{task_id}"
    ]
    
    log_group = '/ecs/content-crew'
    
    try:
        # List available log streams for this specific task
        task_id = task_arn.split('/')[-1]
        streams = logs.describe_log_streams(
            logGroupName=log_group,
            logStreamNamePrefix=f"ecs/crew/{task_id}"
        )
        if streams['logStreams']:
            log_stream = streams['logStreams'][0]['logStreamName']
            print(f"Found log stream: {log_stream}")
        else:
            print("No log streams found")
            sys.exit(1)
        
        events = logs.get_log_events(
            logGroupName=log_group,
            logStreamName=log_stream
        )
        
        # Combine all log messages
        output = '\n'.join([event['message'] for event in events['events']])
        
        # Print to console
        print("\n" + "="*50)
        print("CREW OUTPUT:")
        print("="*50)
        print(output)
        
        # Save to JSON
        result = {
            'task_arn': task_arn,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'topic': topic,
            'output': output
        }
        
        with open('test_results.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nResults saved to test_results.json")
        
    except Exception as e:
        print(f"Error fetching logs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_crew_deployment()