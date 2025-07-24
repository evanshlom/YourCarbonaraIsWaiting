from crewai import Crew, Agent, Task, Process, LLM
from crewai.project import CrewBase, agent, task, crew
import os

# Enable verbose logging
os.environ['LITELLM_LOG'] = 'DEBUG'

@CrewBase
class MarketingCrew:
    """Content Marketing Crew"""
    
    agents_config = 'config/agents.yml'
    tasks_config = 'config/tasks.yml'
    
    def __init__(self):
        self.llm = LLM(
            model="bedrock/amazon.titan-text-express-v1",
            aws_region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )
    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            llm=self.llm
        )
    
    @agent
    def analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['analyzer'],
            llm=self.llm
        )
    
    @agent
    def strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['strategist'],
            llm=self.llm
        )
    
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.researcher()
        )
    
    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            agent=self.analyzer()
        )
    
    @task
    def strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['strategy_task'],
            agent=self.strategist()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )