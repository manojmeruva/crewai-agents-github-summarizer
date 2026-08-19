from langchain.tools import StructuredTool
from mcp_manager.utils import mcp_tool
def list_repo_files(owner: str, repo: str, path: str = ".") -> list:
    """
    List files and folders at a given path in a GitHub repository.
    """
    print(f"Repo Structure Lister: Get files at {path} for {owner}/{repo}")
    result = mcp_tool([
        "tools", "get_file_contents",
        "--owner", owner,
        "--repo", repo,
        "--path", path
    ])
    return result if isinstance(result, list) else []

get_repo_files = StructuredTool.from_function(
    name="get_repo_files",
    func=list_repo_files,
    description="List files and folders at a given path in a GitHub repository using the MCP server"
)