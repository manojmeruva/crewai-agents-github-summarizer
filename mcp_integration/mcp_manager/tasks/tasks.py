from crewai import Task
from ..agents.agents import repo_structure_auditor
from ..tools.directory_scanner import get_repo_files

# Analyze Repository
def analyze_repo_structure_task(owner: str, repo: str):
    return [
        Task(
            description = (
                f"Use the 'get_repo_files' tool to explore the directory structure of the {owner}/{repo} repository. "
                "Generate a Markdown-formatted file tree that shows the layout of files and folders. "
                "For each file, include a bullet point linking to its GitHub `html_url`. "
                "Do not include files like `.gitignore` unless they are significant. "
                "Provide a readable and navigable tree summary that helps someone quickly understand the repo structure."
            ),
            expected_output = (
                f"A Markdown-formatted file tree with clickable links for each file in the {owner}/{repo} repository. "
                "Only list top-level and meaningful subfolders. Use indentation or bullet points to represent hierarchy."
            ),
            agent = repo_structure_auditor,
            tools = [get_repo_files],
            output_file = "/generated_docs/repo_structure.md",
            create_directory = True,
            verbose = True
        )
    ]