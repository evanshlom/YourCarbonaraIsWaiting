from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import json

from .tools import read_customers_from_s3, send_email

class EmailState(TypedDict):
    customers: List[dict]
    emails_to_send: List[dict]
    results: List[str]

def fetch_customers(state: EmailState) -> EmailState:
    """Fetch customer data from S3"""
    customers = read_customers_from_s3()
    return {"customers": customers}

def create_emails(state: EmailState) -> EmailState:
    """Create personalized emails for each customer"""
    emails = []
    
    for customer in state["customers"]:
        if customer["segment"] == "re-engagement":
            subject = f"We miss your {customer['favorite_dish']}, {customer['name'].split()[0]}!"
            body = f"Hi {customer['name'].split()[0]}, it's been {customer['days_since_visit']} days since you enjoyed our {customer['favorite_dish']}. Come back for 20% off!"
        
        elif customer["segment"] == "loyal":
            subject = f"VIP Reward for {customer['name'].split()[0]} 🎉"
            body = f"Hi {customer['name'].split()[0]}, as a loyal customer with {customer['visit_count']} visits, enjoy a free dessert with your next {customer['favorite_dish']}!"
        
        else:  # new_customer
            subject = f"Come back soon, {customer['name'].split()[0]}!"
            body = f"Hi {customer['name'].split()[0]}, we loved serving you! Bring friends and get 25% off your group's meal."
        
        emails.append({
            "to": customer["email"],
            "name": customer["name"],
            "subject": subject,
            "body": body
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