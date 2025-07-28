# generate square data
import json
import boto3
from datetime import datetime, timedelta
import random

# Square POS data generator
def generate_square_data():
    # Base timestamp
    now = datetime.now()
    
    # Customer contacts
    customers = [
        {
            "id": "CUST_SARAH_001",
            "given_name": "Sarah",
            "family_name": "Thompson",
            "email_address": "evshlom@gmail.com",
            "phone_number": "+15555551234",
            "created_at": (now - timedelta(days=180)).isoformat(),
            "updated_at": now.isoformat(),
            "address": {
                "address_line_1": "123 Main St",
                "locality": "San Francisco",
                "administrative_district_level_1": "CA",
                "postal_code": "94105",
                "country": "US"
            }
        },
        {
            "id": "CUST_JOHN_002",
            "given_name": "John",
            "family_name": "Smith",
            "email_address": "evshlom@gmail.com",
            "phone_number": "+17025552345",
            "created_at": (now - timedelta(days=365)).isoformat(),
            "updated_at": now.isoformat(),
            "address": {
                "address_line_1": "456 Las Vegas Blvd",
                "locality": "Las Vegas",
                "administrative_district_level_1": "NV",
                "postal_code": "89109",
                "country": "US"
            }
        },
        {
            "id": "CUST_ARFONZO_003",
            "given_name": "Arfonzo",
            "family_name": "Williams",
            "email_address": "evshlom@gmail.com",
            "phone_number": "+15555553456",
            "created_at": (now - timedelta(days=90)).isoformat(),
            "updated_at": now.isoformat(),
            "address": {
                "address_line_1": "789 Pine St",
                "locality": "San Francisco",
                "administrative_district_level_1": "CA",
                "postal_code": "94108",
                "country": "US"
            }
        }
    ]
    
    # Customer orders
    orders = [
        # Sarah Thompson's orders - 2 carbonara orders
        {
            "id": "ORD_001",
            "customer_id": "CUST_SARAH_001",
            "created_at": (now - timedelta(days=150)).isoformat(),
            "updated_at": (now - timedelta(days=150)).isoformat(),
            "state": "COMPLETED",
            "total_money": {
                "amount": 2200,
                "currency": "USD"
            },
            "line_items": [
                {
                    "uid": "LI_001",
                    "name": "Carbonara Pasta",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1800,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 1800,
                        "currency": "USD"
                    }
                },
                {
                    "uid": "LI_002",
                    "name": "House Salad",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 400,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 400,
                        "currency": "USD"
                    }
                }
            ]
        },
        {
            "id": "ORD_002",
            "customer_id": "CUST_SARAH_001",
            "created_at": (now - timedelta(days=45)).isoformat(),
            "updated_at": (now - timedelta(days=45)).isoformat(),
            "state": "COMPLETED",
            "total_money": {
                "amount": 1800,
                "currency": "USD"
            },
            "line_items": [
                {
                    "uid": "LI_003",
                    "name": "Carbonara Pasta",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1800,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 1800,
                        "currency": "USD"
                    }
                }
            ]
        },
        # John Smith's orders - 3 All American Burger orders
        {
            "id": "ORD_003",
            "customer_id": "CUST_JOHN_002",
            "created_at": (now - timedelta(days=120)).isoformat(),
            "updated_at": (now - timedelta(days=120)).isoformat(),
            "state": "COMPLETED",
            "total_money": {
                "amount": 1500,
                "currency": "USD"
            },
            "line_items": [
                {
                    "uid": "LI_004",
                    "name": "All American Burger",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1200,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 1200,
                        "currency": "USD"
                    }
                },
                {
                    "uid": "LI_005",
                    "name": "French Fries",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 300,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 300,
                        "currency": "USD"
                    }
                }
            ]
        },
        {
            "id": "ORD_004",
            "customer_id": "CUST_JOHN_002",
            "created_at": (now - timedelta(days=60)).isoformat(),
            "updated_at": (now - timedelta(days=60)).isoformat(),
            "state": "COMPLETED",
            "total_money": {
                "amount": 1500,
                "currency": "USD"
            },
            "line_items": [
                {
                    "uid": "LI_006",
                    "name": "All American Burger",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1200,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 1200,
                        "currency": "USD"
                    }
                },
                {
                    "uid": "LI_007",
                    "name": "Onion Rings",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 300,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 300,
                        "currency": "USD"
                    }
                }
            ]
        },
        {
            "id": "ORD_005",
            "customer_id": "CUST_JOHN_002",
            "created_at": (now - timedelta(days=15)).isoformat(),
            "updated_at": (now - timedelta(days=15)).isoformat(),
            "state": "COMPLETED",
            "total_money": {
                "amount": 1200,
                "currency": "USD"
            },
            "line_items": [
                {
                    "uid": "LI_008",
                    "name": "All American Burger",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1200,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 1200,
                        "currency": "USD"
                    }
                }
            ]
        },
        # Arfonzo Williams' order - 1 visit, 3 entrees (family/group)
        {
            "id": "ORD_006",
            "customer_id": "CUST_ARFONZO_003",
            "created_at": (now - timedelta(days=75)).isoformat(),
            "updated_at": (now - timedelta(days=75)).isoformat(),
            "state": "COMPLETED",
            "total_money": {
                "amount": 5400,
                "currency": "USD"
            },
            "line_items": [
                {
                    "uid": "LI_009",
                    "name": "Grilled Salmon",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 2200,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 2200,
                        "currency": "USD"
                    }
                },
                {
                    "uid": "LI_010",
                    "name": "Chicken Parmesan",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 1800,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 1800,
                        "currency": "USD"
                    }
                },
                {
                    "uid": "LI_011",
                    "name": "Steak Frites",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 2600,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 2600,
                        "currency": "USD"
                    }
                },
                {
                    "uid": "LI_012",
                    "name": "Kids Mac & Cheese",
                    "quantity": "1",
                    "base_price_money": {
                        "amount": 800,
                        "currency": "USD"
                    },
                    "total_money": {
                        "amount": 800,
                        "currency": "USD"
                    }
                }
            ]
        }
    ]
    
    return customers, orders

def upload_to_s3(bucket_name='aiawsattack-bucket'):
    s3 = boto3.client('s3')
    customers, orders = generate_square_data()
    
    # Upload customer contacts
    s3.put_object(
        Bucket=bucket_name,
        Key='square_data/raw/customer_contacts.json',
        Body=json.dumps(customers, indent=2)
    )
    
    # Upload customer orders
    s3.put_object(
        Bucket=bucket_name,
        Key='square_data/raw/customer_orders.json',
        Body=json.dumps(orders, indent=2)
    )
    
    print(f"Uploaded customer data to s3://{bucket_name}/square_data/raw/")

if __name__ == "__main__":
    upload_to_s3()