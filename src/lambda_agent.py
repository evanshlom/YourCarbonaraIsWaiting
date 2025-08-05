import json

def lambda_handler(event, context):
    """
    Lambda handler for Bedrock Agent email generation
    """
    # Parse the agent input
    agent_input = json.loads(event.get('inputText', '{}'))
    customer = agent_input.get('customer', {})
    
    # Determine discount based on customer segment
    discount_map = {
        're-engagement': '25',  # Higher for win-back
        'loyal': '20',          # Moderate for loyal
        'new_customer': '30'    # Highest for acquisition
    }
    
    segment = customer.get('segment', 'new_customer')
    discount = discount_map.get(segment, '20')
    
    # Adjust based on days since visit
    days_since = customer.get('days_since_visit', 0)
    if days_since > 60:
        discount = str(min(int(discount) + 5, 30))
    
    # Generate email
    first_name = customer.get('name', 'Valued Customer').split()[0]
    favorite = customer.get('favorite_dish', 'your favorite dish')
    
    if segment == 're-engagement':
        subject = f"We miss your {favorite}, {first_name}!"
        body = f"Hi {first_name},\n\nIt's been {days_since} days since you enjoyed our {favorite}. Come back for {discount}% off! We've missed you.\n\nSee you soon!"
    elif segment == 'loyal':
        subject = f"VIP {discount}% off for {first_name} 🎉"
        body = f"Hi {first_name},\n\nAs a loyal customer with {customer.get('visit_count', 0)} visits, enjoy {discount}% off your next {favorite}!\n\nThank you for being awesome!"
    else:
        subject = f"Come back soon, {first_name}!"
        body = f"Hi {first_name},\n\nWe loved serving you! Bring friends and get {discount}% off your group's meal.\n\nHope to see you again!"
    
    # Return formatted response for agent
    return {
        'statusCode': 200,
        'body': json.dumps({
            'subject': subject,
            'body': body,
            'discount': discount
        })
    }