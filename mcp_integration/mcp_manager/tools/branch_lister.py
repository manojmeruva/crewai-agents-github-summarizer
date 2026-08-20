from langchain.tools import StructuredTool
from mcp_manager.utils import mcp_tool

def list_branches( owner: str, repo: str) -> list:
        """Uses mcp_tool to get a list of repo branches."""
        print(f"Branch Lister: Get the branches of {owner}/{repo}")
        result = mcp_tool(['tools', 'list_branches', '--owner', owner, '--repo', repo, '--perPage', '5',  '--page', '1'])
        if isinstance(result, list):
            return result
        else:
            print(f"Pull Request Lister: Unexpected result: {result}")
            return []

get_repo_branches = StructuredTool.from_function(
    name = "get_repo_branches",
    func = list_branches,
    description="'Fetch and provide a list of 5 branches of the GitHub repository using the MCP server."
)