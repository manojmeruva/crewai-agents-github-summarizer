from crewai import Crew, Process
from ..tasks.tasks import analyze_repo_structure_task
from ..agents.agents import repo_structure_auditor

def build_crew(owner: str, repo: str) -> Crew:
    tasks = []
    tasks.extend (analyze_repo_structure_task(owner,repo))

    return Crew(
        agents = [repo_structure_auditor],
        tasks = tasks, 
        process = Process.sequential,
        verbose = True,
        cache = True,
    )