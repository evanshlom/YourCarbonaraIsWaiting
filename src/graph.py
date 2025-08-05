from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import json
import boto3
import os

from .tools import read_customers_from_s3, send_email

class EmailState(TypedDict):
    customers: List[dict]
    emails_to_send: List[dict]
    results: List[str]

# Initialize Bedrock Agent client
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

def fetch_customers(state: EmailState) -> EmailState:
    """Fetch customer data from S3"""
    customers = read_customers_from_s3()
    return {"customers": customers}

def create_emails(state: EmailState) -> EmailState:
    """Use AgentCore to create personalized emails for each customer"""
    emails = []
    
    for customer in state["customers"]:
        try:
            # Use inline agent for email generation with discount
            response = bedrock_agent.invoke_inline_agent(
                inputText=f"""Generate personalized marketing email for restaurant customer:
                {json.dumps(customer)}
                
                Determine appropriate discount (10-30%) based on their profile.
                Return JSON: {{"subject": "...", "body": "...", "discount": "20"}}""",
                
                foundationModel='anthropic.claude-instant-v1',
                
                instruction="""You are a restaurant marketing agent. Create personalized emails 
                that mention the customer's favorite dish and include an appropriate discount. 
                Keep emails under 100 words, friendly and casual. Always return valid JSON.""",
                
                enableTrace=False,
                sessionId=f"email-{customer['name'].replace(' ', '-')}"
            )
            
            # Parse response
            completion = response.get('completion', '{}')
            email_data = json.loads(completion)
            
            emails.append({
                "to": customer["email"],
                "name": customer["name"],
                "subject": email_data.get('subject', f"Special offer for {customer['name'].split()[0]}!"),
                "body": email_data.get('body', f"Hi {customer['name'].split()[0]}, enjoy {email_data.get('discount', '20')}% off your next {customer['favorite_dish']}!")
            })
            
            print(f"Generated email for {customer['name']} with {email_data.get('discount', '20')}% discount")
            
        except Exception as e:
            print(f"AgentCore error for {customer['name']}: {e}")
            # Fallback email
            emails.append({
                "to": customer["email"],
                "name": customer["name"],
                "subject": f"We miss you, {customer['name'].split()[0]}!",
                "body": f"Hi {customer['name'].split()[0]},\n\nIt's been {customer['days_since_visit']} days since you enjoyed our {customer['favorite_dish']}. Come back for 20% off!\n\nSee you soon!"
            })
    
    return {"emails_to_send": emails}

def send_emails(state: EmailState) -> EmailState:
    """Send all emails"""
    results = []
    
    for email in state["emails_to_send"]:
        result = send_email(
            to_email=email["to"],
            subject=email["subject"],
            body=email["body"],
            customer_name=email["name"]
        )
        results.append(result)
    
    return {"results": results}

# Build the graph
def create_email_graph():
    workflow = StateGraph(EmailState)
    
    # Add nodes
    workflow.add_node("fetch_customers", fetch_customers)
    workflow.add_node("create_emails", create_emails)
    workflow.add_node("send_emails", send_emails)
    
    # Add edges
    workflow.set_entry_point("fetch_customers")
    workflow.add_edge("fetch_customers", "create_emails")
    workflow.add_edge("create_emails", "send_emails")
    workflow.add_edge("send_emails", END)
    
    return workflow.compile()