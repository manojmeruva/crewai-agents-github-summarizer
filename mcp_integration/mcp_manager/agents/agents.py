import os
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from ..tools.directory_scanner import get_repo_files
from ..tools.issue_retriever import get_issue
from ..tools.pull_request_lister import get_pull_requests
from ..tools.branch_lister import get_repo_branches

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

## Repository Structure Analyzer
repo_structure_auditor = Agent(
    role="Repository Structure Auditor",
    goal="Analyze the folder and file structure of a GitHub repository and produce a Markdown-based file tree with clickable links.",
    backstory=(
        "You are skilled at visualizing repository structures. You help developers by generating clean, readable "
        "Markdown summaries of files and folders, especially for documentation purposes."
    ),
    tools=[get_repo_files],
    llm=llm,
    verbose=True
)

## GitHub Issue Analyst
issue_analyst = Agent(
    role = "GitHub Issue Analyst",
    goal = "Fetch and summarize open GitHub issues, and suggest which issue should be prioritized.",
    backstory = (
        "You are an experienced open-source contributor who can identify, retrieve, and analyze GitHub issues. "
        "You know how to summarize them effectively and highlight the ones that need urgent attention."
    ),
    tools = [get_issue],
    llm=llm,
    verbose = True
)

## Pull Requests Lister
pull_requests_fetcher_reporter = Agent(
    role = "Pull Request Lister",
    goal = "Fetch and provide a list of 5 most recently created pull requests from a GitHub repository.",
    backstory = "You are an expert in retrieving information about GitHub issues using the MCP server. You also concisely summarize open issues as categories and provide a comprehensive and readable report",
    tools = [get_pull_requests],
    llm=llm,
    verbose = True
)

## Branch Lister
repo_branch_reporter = Agent(
    role = "Repository Branch Reportor",
    goal = "Fetch and provide a list of 5 branches in a GitHub repository.",
    backstory = "You are an expert in retrieving information about GitHub issues using the MCP server. You also concisely summarize branch as categories and provide a comprehensive and readable report",
    tools = [get_repo_branches],
    llm=llm,
    verbose = True
)