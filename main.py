import os
import json
import sys
from src.crew import MarketingCrew

def run():
    # Get input from environment variable (set by API Gateway mapping)
    input_data = os.environ.get('INPUT_DATA', '{}')
    
    try:
        data = json.loads(input_data)
        topic = data.get('topic', 'I want to create rugpull reaction videos. Focus on crypto, poopcoins, and nfts.')
    except:
        topic = 'I want to create rugpull reaction videos. Focus on crypto, poopcoins, and nfts.'
    
    inputs = {'topic': topic}
    
    crew = MarketingCrew().crew()
    try:
        result = crew.kickoff(inputs=inputs)
    except Exception as e:
        print(f"FULL ERROR: {type(e).__name__}: {str(e)}")
        raise
    
    # Output as JSON for API Gateway
    output = {
        'statusCode': 200,
        'body': json.dumps({
            'result': str(result),
            'topic': topic
        })
    }
    
    print(json.dumps(output))
    
    # Exit after completion so container stops
    sys.exit(0)

if __name__ == "__main__":
    run()