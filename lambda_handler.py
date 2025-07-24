import json
import time
from src.crew import MarketingCrew

# Manual setup Sqlite3 to avoid weird error lambda fcn was defaulting to outdated version of sqlite3 (also added line to Dockerfile for this)
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

def lambda_handler(event, context):
    start_time = time.time()
    
    # Get topic from event or use default
    topic = event.get('topic', 'I want to create rugpull reaction videos. Focus on crypto, poopcoins, and nfts.')
    
    # Log structured data for CloudWatch
    print(json.dumps({
        "event": "crew_start",
        "topic": topic,
        "request_id": context.request_id
    }))
    
    try:
        crew = MarketingCrew().crew()
        result = crew.kickoff(inputs={'topic': topic})
        
        # Log completion with metrics
        print(json.dumps({
            "event": "crew_complete",
            "duration": time.time() - start_time,
            "topic": topic,
            "request_id": context.request_id,
            "result_length": len(str(result))
        }))
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'result': str(result),
                'topic': topic,
                'duration': time.time() - start_time
            })
        }
    
    except Exception as e:
        print(json.dumps({
            "event": "crew_error",
            "error": str(e),
            "topic": topic,
            "request_id": context.request_id
        }))
        raise