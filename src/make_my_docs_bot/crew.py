from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from make_my_docs_bot.tools.branch_change_analyzer import BranchChangeAnalyzerTool
from make_my_docs_bot.tools.korean_reverse_mapping import KoreanFileMappingTool
from make_my_docs_bot.tools.portuguese_brazil_reverse_mapping import PortugureseBrazilFileMappingTool
from make_my_docs_bot.tools.read_write_tool import FileContentUpdaterTool
from make_my_docs_bot.tools.github_commit_tool import GitCommitTool
from make_my_docs_bot.tools.file_indexing import FileIndexingTool
from make_my_docs_bot.tools.index_fixer import FileIndexFixerTool
from make_my_docs_bot.pydantic_models import SectionChanges, FileChanges, FileContentUpdates

@CrewBase
class MakeMyDocsBot():
    """MakeMyDocsBot crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def index_mapping_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['index_mapping_specialist'], # type: ignore[index]
            verbose=True,
            tools=[
				FileIndexingTool()
            ]
        )
    
    @agent
    def index_mapping_fixer(self) -> Agent:
        return Agent(
            config=self.agents_config['index_mapping_fixer'], # type: ignore[index]
            verbose=True,
            tools=[
                FileIndexFixerTool()
            ]
        )

    @agent
    def documentation_change_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['documentation_change_analyzer'], # type: ignore[index]
            verbose=True,
            tools=[
				BranchChangeAnalyzerTool()
            ]
        )

    @agent
    def korean_translator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['korean_translator_agent'], # type: ignore[index]
            verbose=True,
            tools=[
				KoreanFileMappingTool()
            ]
        )
    
    @agent
    def portuguese_brazil_translator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['portuguese_brazil_translator_agent'], # type: ignore[index]
            verbose=True,
            tools=[
				PortugureseBrazilFileMappingTool()
            ]
        )
    
    @agent
    def file_content_editor_and_git_commiter_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['file_content_editor_and_git_commiter_agent'], # type: ignore[index]
            verbose=True,
            tools=[
				FileContentUpdaterTool(),
                GitCommitTool()
            ]
        )


    @task
    def validate_file_structure_task(self) -> Task:
        return Task(
            config=self.tasks_config['validate_file_structure_task'],
            output_pydantic=SectionChanges # type: ignore[index]
        )
    
    @task
    def index_fixing_task(self) -> Task:
        return Task(
            config=self.tasks_config['index_fixing_task'], # type: ignore[index]
        )

    @task
    def analyze_branch_documentation_changes_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_branch_documentation_changes_task'],
            output_pydantic=FileChanges # type: ignore[index]
        )
    
    @task
    def korean_documentation_translator_task(self) -> Task:
        return Task(
            config=self.tasks_config['korean_documentation_translator_task'],
            output_pydantic=FileContentUpdates # type: ignore[index]
        )
    
    @task
    def portuguese_brazil_documentation_translator_task(self) -> Task:
        return Task(
            config=self.tasks_config['portuguese_brazil_documentation_translator_task'],
            output_pydantic=FileContentUpdates # type: ignore[index] # type: ignore[index]
        )
    
    @task
    def file_content_editor_and_git_commiter_task(self) -> Task:
        return Task(
            config=self.tasks_config['file_content_editor_and_git_commiter_task'], # type: ignore[index]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the MakeMyDocsBot crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            tracing=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
