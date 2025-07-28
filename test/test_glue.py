#test glue pipeline
import boto3
import time
import json

def test_glue_pipeline():
    """Test the complete data pipeline"""
    
    glue = boto3.client('glue', region_name='us-east-1')
    s3 = boto3.client('s3', region_name='us-east-1')
    
    bucket_name = 'aiawsattack-bucket'
    
    print("1. Generating and uploading Square POS data...")
    from generate_square_data import upload_to_s3
    upload_to_s3(bucket_name)
    
    print("2. Starting Glue job...")
    response = glue.start_job_run(JobName='square-data-transform')
    run_id = response['JobRunId']
    print(f"   Glue job run ID: {run_id}")
    
    print("3. Waiting for Glue job to complete...")
    while True:
        status = glue.get_job_run(JobName='square-data-transform', RunId=run_id)
        state = status['JobRun']['JobRunState']
        print(f"   Status: {state}")
        
        if state in ['SUCCEEDED', 'FAILED', 'STOPPED']:
            break
        
        time.sleep(10)
    
    if state == 'SUCCEEDED':
        print("4. Glue job completed successfully!")
        
        # Check processed data
        print("5. Checking processed data in S3...")
        try:
            # List objects in processed folder
            response = s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix='square_data/processed/agent_view/'
            )
            
            if 'Contents' in response:
                print(f"   Found {len(response['Contents'])} processed files")
                
                # Download and display sample data
                key = response['Contents'][0]['Key']
                obj = s3.get_object(Bucket=bucket_name, Key=key)
                data = obj['Body'].read().decode('utf-8')
                
                print("\n   Sample processed data:")
                # Parse JSON lines
                for i, line in enumerate(data.strip().split('\n')[:3]):
                    if line:
                        customer = json.loads(line)
                        print(f"\n   Customer {i+1}:")
                        print(f"   - Name: {customer['given_name']} {customer['family_name']}")
                        print(f"   - Segment: {customer['customer_segment']}")
                        print(f"   - Favorite: {customer.get('favorite_product', 'N/A')}")
                        print(f"   - Priority: {customer['engagement_priority']}")
            else:
                print("   No processed data found!")
        except Exception as e:
            print(f"   Error checking data: {e}")
    else:
        print(f"4. Glue job failed with state: {state}")
        if 'ErrorMessage' in status['JobRun']:
            print(f"   Error: {status['JobRun']['ErrorMessage']}")

if __name__ == "__main__":
    test_glue_pipeline()