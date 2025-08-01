FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install boto3 python-dotenv

# Copy test runner
COPY run_final_test.py .
COPY .env .

# Run the complete email campaign
CMD ["python", "test.py"]