from src.graph import create_email_graph
import json

def main():
    print("Starting Restaurant Email Campaign...")
    
    # Create and run the graph
    app = create_email_graph()
    
    # Run with empty initial state
    result = app.invoke({
        "customers": [],
        "emails_to_send": [],
        "results": []
    })
    
    # Print results
    print("\nCampaign Results:")
    print(f"Emails sent: {len(result['results'])}")
    for r in result['results']:
        print(f"  - {r}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()