from langchain.tools import StructuredTool
from mcp_manager.utils import mcp_tool

def list_pull_requests( owner: str, repo: str) -> list:
        """Uses mcp_tool to get a list of pull requests."""
        print(f"Pull Requests Lister: Get the pull requests issues for {owner}/{repo}")
        result = mcp_tool(['tools', 'list_pull_requests', '--owner', owner, '--repo', repo, '--sort', "updated", '--direction', 'desc', '--perPage', '5',  '--page', '1'])
        if isinstance(result, list):
            return result
        else:
            print(f"Pull Request Lister: Unexpected result: {result}")
            return []

get_pull_requests = StructuredTool.from_function(
    name = "get_pull_requests",
    func = list_pull_requests,
    description = "'Fetch and provide a list of 5 most recently created pull requests from a GitHub repository using the MCP server."
)