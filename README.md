# YourCarbonaraIsWaiting
AiAwsAttackV2 Agentic Marketing Outreach for Restaurant business.

## AiAwsAttack
### ATTACK AI Agent projects with FAST FLEXIBLE dev+deploy cicd pipeline.

* Crew AI: Popular framework with 1 py file and 2 yml files for rapid config.
* AWS Bedrock: Titan-Express LLM as a starting point for agent crew.
* AWS Lambda Container: Deploy a POC as Lambda function which runs an ECR container. Test by invoking from AWS CLI or Console. (For next steps: connect Lambda function to API Gateway)

## Project Structure
```
content-crew/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── src/
│   ├── __init__.py
│   ├── crew.py
│   └── config/
│       ├── agents.yml
│       └── tasks.yml
├── main.py
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

## Quick Start

### CICD Secrets
Add these to GitHub Actions Secrets before pushing the CICD pipe:
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* (The CICD yml file uses AWS Region us-east-1)

### Deploy to AWS Lambda
```bash
# CI/CD creates everything automatically
git add .
git commit -m "Deploy"
git push origin main
```

### Test the Lambda Deployment
It takes 30-60 seconds for function to run and return 200 response after invoked. Then run cat output.json to see the full output.
```bash
# Default topic
aws lambda invoke --function-name content-strategy-crew output.json

# Custom topic
aws lambda invoke \
  --function-name content-strategy-crew \
  --payload '{"topic": "'I want to create rugpull reaction videos. Focus on crypto, poopcoins, and nfts.'"}' \
  output.json

cat output.json
```

## Agentic Workflow

Three-agent workflow:
1. **Researcher**: Finds similar creators across platforms
2. **Analyzer**: Ranks platforms by opportunity
3. **Strategist**: Creates 30-day content plan

Stack: CrewAI + AWS Bedrock (Titan Express) + Lambda Container