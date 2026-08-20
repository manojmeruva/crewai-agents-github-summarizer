from langchain.tools import StructuredTool
from mcp_manager.utils import mcp_tool

def get_open_issues( owner: str, repo: str) -> list:
        """Uses mcp_tool to get a list of open issues."""
        print(f"Issue Retriever: Getting open issues for {owner}/{repo}")
        result = mcp_tool(['tools', 'list_issues', '--owner', owner, '--repo', repo, '--state', 'open', '--perPage', '5',  '--page', '1'])
        if isinstance(result, list):
            return result
        else:
            print(f"Issue Retriever: Unexpected result: {result}")
            return []

get_issue = StructuredTool.from_function(
    name = "get_issue",
    func = get_open_issues,
    description = "'Fetch and provide a list of open issues from a GitHub repository using the MCP server."
    )