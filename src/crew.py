from crewai import Crew, Agent, Task, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai.tools import tool
import os
import boto3
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Enable verbose logging
os.environ['LITELLM_LOG'] = 'DEBUG'

@CrewBase
class RestaurantCrew:
    """Restaurant Email Marketing Crew"""
    
    agents_config = 'config/agents.yml'
    tasks_config = 'config/tasks.yml'
    
    def __init__(self):
        self.llm = LLM(
            model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
            aws_region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        # Initialize S3 client
        self.s3 = boto3.client('s3', region_name='us-east-1')
        
        # Create tools
        self.customer_data_tool = self._create_customer_data_tool()
        self.email_tool = self._create_email_tool()
    
    def _create_customer_data_tool(self):
        """Tool to fetch customer data from S3"""
        @tool("fetch_customer_data")
        def fetch_customer_data(query: str = "all") -> str:
            """Fetch customer insights data from S3 processed by Glue"""
            try:
                # List all files in the processed folder
                response = self.s3.list_objects_v2(
                    Bucket='aiawsattack-bucket',
                    Prefix='square_data/processed/agent_view/'
                )
                
                if 'Contents' not in response:
                    return json.dumps({"error": "No processed data found in S3"})
                
                # Read all part files
                customers = []
                for obj in response['Contents']:
                    if obj['Key'].endswith('.json'):
                        file_response = self.s3.get_object(
                            Bucket='aiawsattack-bucket',
                            Key=obj['Key']
                        )
                        data = file_response['Body'].read().decode('utf-8')
                        
                        # Parse JSON lines format (each line is a JSON object)
                        for line in data.strip().split('\n'):
                            if line:
                                customers.append(json.loads(line))
                
                if not customers:
                    return json.dumps({"error": "No customer data found"})
                
                return json.dumps(customers, indent=2)
                
            except Exception as e:
                return json.dumps({"error": f"Failed to fetch data: {str(e)}"})
        
        return fetch_customer_data
    
    def _create_email_tool(self):
        """Tool to send emails via SMTP"""
        @tool("send_email")
        def send_email(to_email: str, subject: str, body: str, customer_name: str) -> str:
            """Send personalized email to customer"""
            try:
                # Email configuration
                smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
                smtp_port = int(os.environ.get('SMTP_PORT', '587'))
                sender_email = os.environ.get('SENDER_EMAIL', 'restaurant@example.com')
                sender_password = os.environ.get('SENDER_PASSWORD', 'app_password')
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = f"The Restaurant <{sender_email}>"
                msg['To'] = to_email
                msg['Subject'] = subject
                
                # Add body
                msg.attach(MIMEText(body, 'plain'))
                
                # Send email
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                
                return f"Email sent successfully to {customer_name} at {to_email}"
            
            except Exception as e:
                # For testing, just log the email
                print(f"\n--- EMAIL TO: {customer_name} ({to_email}) ---")
                print(f"SUBJECT: {subject}")
                print(f"BODY:\n{body}")
                print("--- END EMAIL ---\n")
                return f"Email logged for {customer_name} (not sent - test mode)"
        
        return send_email
    
    @agent
    def customer_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_analyst'],
            llm=self.llm,
            tools=[self.customer_data_tool]
        )
    
    @agent
    def email_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['email_writer'],
            llm=self.llm
        )
    
    @agent
    def email_sender(self) -> Agent:
        return Agent(
            config=self.agents_config['email_sender'],
            llm=self.llm,
            tools=[self.email_tool]
        )
    
    @task
    def analyze_customers_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_customers_task'],
            agent=self.customer_analyst()
        )
    
    @task
    def write_emails_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_emails_task'],
            agent=self.email_writer()
        )
    
    @task
    def send_emails_task(self) -> Task:
        return Task(
            config=self.tasks_config['send_emails_task'],
            agent=self.email_sender()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            function_calling_llm=self.llm
        )