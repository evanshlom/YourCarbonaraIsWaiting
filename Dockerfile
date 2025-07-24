FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install pysqlite3-binary && pip install -r requirements.txt

COPY src/ ./src/
COPY main.py .

CMD ["python", "main.py"]