from crewai import Crew, Process
from ..tasks.tasks import analyze_repo_structure_task, get_issue_tasks, list_pull_requests_tasks, list_branches_tasks
from ..agents.agents import repo_structure_auditor, issue_analyst, pull_requests_fetcher_reporter, repo_branch_reporter

def build_crew(owner: str, repo: str, callbacks: dict = None) -> Crew:
    callbacks = callbacks or {}
    tasks = []
    tasks.extend(analyze_repo_structure_task(owner, repo, on_done=callbacks.get("structure")))
    tasks.extend(get_issue_tasks(owner, repo, on_done=callbacks.get("issues")))
    tasks.extend(list_pull_requests_tasks(owner, repo, on_done=callbacks.get("pulls")))
    tasks.extend(list_branches_tasks(owner, repo, on_done=callbacks.get("branches")))

    return Crew(
        agents = [repo_structure_auditor, issue_analyst, pull_requests_fetcher_reporter, repo_branch_reporter],
        tasks = tasks, 
        process = Process.sequential,
        verbose = True,
        cache = True,
    )