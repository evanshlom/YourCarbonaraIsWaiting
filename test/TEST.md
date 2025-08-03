# Quick Commands

## First Time Setup
Edit .env with your AWS credentials

## Run Email Campaign
- Add your AWS secrets to repo (Git Actions)
- Push cicd to deploy resources on AWS
- Then run below commands
```bash
aws ses verify-email-identity --email-address evshlom@gmail.com --region us-east-1
# Check email inbox for verification email and confirm
cd test
docker build -t test .
docker run test
```

## One-liner (after .env is configured)
```bash
docker build -t campaign-runner . && docker run campaign-runner
```