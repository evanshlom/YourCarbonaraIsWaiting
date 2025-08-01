# Quick Commands

## First Time Setup
Edit .env with your AWS credentials

## Run Email Campaign
```bash
cd test
docker build -t test .
docker run test
```

## One-liner (after .env is configured)
```bash
docker build -t campaign-runner . && docker run campaign-runner
```