# YourCarbonaraIsWaiting

Restaurant email marketing system using LangGraph to send personalized emails to customers based on their dining history. **POC**

## Project Structure

```
YourCarbonaraIsWaiting/
├── .github/
│   └── workflows/
│       └── deploy.yml       # CI/CD pipeline for AWS deployment
├── data/
│   └── customers.json       # Processed customer data (POC Data)
├── src/
│   ├── __init__.py         # Package initialization
│   ├── graph.py            # LangGraph email workflow
│   └── tools.py            # S3 reader and email sender tools
├── main.py                 # Application entry point
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

- **LangGraph Workflow**: Simple 3-step pipeline (fetch → create → send)
- **Customer Segmentation**: Targets re-engagement, loyal, and new customers
- **Personalized Emails**: Custom messages based on dining history
- **AWS Integration**: Runs on ECS Fargate with S3 data storage

## Demo Instructions

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd YourCarbonaraIsWaiting
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set AWS credentials**
   ```bash
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

4. **Upload test data to S3**
   ```bash
   aws s3 cp data/customers.json s3://aiawsattack-bucket/
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

### Docker Local Testing

1. **Build the image**
   ```bash
   docker build -t restaurant-email .
   ```

2. **Run with AWS credentials**
   ```bash
   docker run \
     -e AWS_ACCESS_KEY_ID=your_key \
     -e AWS_SECRET_ACCESS_KEY=your_secret \
     -e AWS_DEFAULT_REGION=us-east-1 \
     restaurant-email
   ```

### AWS Deployment

1. **Set GitHub secrets**
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

2. **Push to main branch**
   ```bash
   git add .
   git commit -m "Deploy email campaign"
   git push origin main
   ```

3. **Run the ECS task manually**
   ```bash
   # Get subnet ID
   SUBNET_ID=$(aws ec2 describe-subnets --query 'Subnets[0].SubnetId' --output text)
   
   # Run task
   aws ecs run-task \
     --cluster restaurant-emails \
     --task-definition restaurant-email \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],assignPublicIp=ENABLED}"
   ```

## Sample Output

```
Starting Restaurant Email Campaign...

--- EMAIL TO: Sarah Thompson (evshlom@gmail.com) ---
SUBJECT: We miss your Carbonara Pasta, Sarah!
BODY:
Hi Sarah, it's been 45 days since you enjoyed our Carbonara Pasta. Come back for 20% off!
--- END EMAIL ---

--- EMAIL TO: John Smith (evshlom@gmail.com) ---
SUBJECT: VIP Reward for John 🎉
BODY:
Hi John, as a loyal customer with 3 visits, enjoy a free dessert with your next All American Burger!
--- END EMAIL ---

--- EMAIL TO: Arfonzo Williams (evshlom@gmail.com) ---
SUBJECT: Come back soon, Arfonzo!
BODY:
Hi Arfonzo, we loved serving you! Bring friends and get 25% off your group's meal.
--- END EMAIL ---

Campaign Results:
Emails sent: 3
  - Email sent to Sarah Thompson
  - Email sent to John Smith
  - Email sent to Arfonzo Williams

Done!
```

## Cost Considerations

- **ECS Fargate**: ~$0.01 per run (256 CPU, 512 MB)
- **S3 Storage**: Minimal (< $0.01/month)
- **ECR**: ~$0.01/month for image storage

## Next Steps

1. **Add real email sending** via SES or SMTP
2. **Schedule runs** with EventBridge
3. **Add monitoring** with CloudWatch
4. **Integrate with real data**