import os
import json
import sys
from src.crew import RestaurantCrew

def run():
    # Restaurant email marketing inputs
    inputs = {
        'restaurant_name': os.environ.get('RESTAURANT_NAME', 'The Gourmet Kitchen'),
        'campaign_goal': 'Re-engage customers and drive repeat visits'
    }
    
    crew = RestaurantCrew().crew()
    
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
            'inputs': inputs
        })
    }
    
    print(json.dumps(output))
    
    # Exit after completion so container stops
    sys.exit(0)

if __name__ == "__main__":
    run()