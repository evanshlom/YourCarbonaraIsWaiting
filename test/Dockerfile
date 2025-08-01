FROM python:3.11-slim

WORKDIR /test

# Install boto3 and python-dotenv
RUN pip install boto3 python-dotenv

# Copy files
COPY run_campaign.py .
COPY .env* ./

# Run the test
CMD ["python", "run_campaign.py"]