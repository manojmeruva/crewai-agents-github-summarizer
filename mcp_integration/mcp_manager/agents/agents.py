from crewai import Agent
from ..tools.directory_scanner import get_repo_files

## Repository Structure Analyzer
repo_structure_auditor = Agent(
    role = "Repository Structure Auditor",
    goal = "Analyze the folder and file structure of a GitHub repository and produce a Markdown-based file tree with clickable links.",
    backstory = (
        "You are skilled at visualizing repository structures. You help developers by generating clean, readable "
        "Markdown summaries of files and folders, especially for documentation purposes."
        ),
        tools = [get_repo_files],
        verbose = True
    )