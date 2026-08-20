import subprocess
import json
import os
import markdown
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from langchain_google_genai import ChatGoogleGenerativeAI
from .crews.crew import build_crew




GITHUB_TOKEN = getattr(settings, 'GITHUB_PERSONAL_ACCESS_TOKEN', None)
GOOGLE_API_KEY = getattr(settings, 'GOOGLE_API_KEY', None)

# The utility function that extracts owner and repo from a GitHub URL
def extract_owner_repo(repo_url):
    parts = repo_url.split('/')
    if len(parts) >= 5 and parts[2] == 'github.com':
        owner = parts[3]
        repo_name = parts[4].replace('.git', '')
        return owner, repo_name
    else:
        raise ValueError("Invalid GitHub repository URL format.")

# The utility function that combines multiple markdown files
def combine_markdown_files(file_paths, output_path, owner, repo_name):
    combined_content = f"# Summary for {owner}/{repo_name}\n\n"
    for file_path in file_paths:
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                markdown_content = ""
                if lines and lines[0].strip() == "```markdown" and len(lines) > 1 and lines[-1].strip() == "```":
                    markdown_content = "".join(lines[1:-1]).strip()
                else:
                    markdown_content = "".join(lines).strip()
                combined_content += f"\n\n---\n\n" + markdown_content
        except FileNotFoundError:
            print(f"Warning: File not found: {file_path}")
    try:
        with open(output_path, "w") as f:
            f.write(combined_content.strip())
        print(f"Combined output saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error saving combined markdown: {e}")
        return None

import markdown

# The utility function to change markdown to HTML
def convert_markdown_to_html(markdown_file_path):
    try:
        with open(markdown_file_path, "r") as f:
            markdown_text = f.read()
            html_content = markdown.markdown(markdown_text, extensions=['extra'])
            return html_content
    except FileNotFoundError:
        print(f"Error: Markdown file not found at {markdown_file_path}")
        return None
    except Exception as e:
        print(f"Error converting Markdown to HTML: {e}")
        return None



def documentation_interface(request):
    return render(request, 'mcp_manager/documentation_interface.html')


def generate_documentation(request):
    if request.method == 'POST':
        repo_url = request.POST.get('repo_url', '')
        if repo_url:
            try:
                owner, repo_name = extract_owner_repo(repo_url)
                if owner and repo_name:
                    if not GOOGLE_API_KEY:
                        error = "Error: GOOGLE_API_KEY is not set in Django settings."
                        return render(request, 'mcp_manager/documentation_interface.html', {'error': error})

                    llm = ChatGoogleGenerativeAI(
                        model="gemma-4-31b-it",
                        google_api_key=os.getenv("GOOGLE_API_KEY"),
                    )
                    crew = build_crew(owner, repo_name)
                    crew.kickoff()

                    output_files = [
                        "/usercode/mcp_integration/generated_docs/repo_structure.md",
                        "/usercode/mcp_integration/generated_docs/report_issues.md",
                        "/usercode/mcp_integration/generated_docs/pull_requests.md",
                        "/usercode/mcp_integration/generated_docs/branches.md"
                    ]
                    final_output_path = "/usercode/mcp_integration/generated_docs/summary.md"
                    combined_markdown_path = combine_markdown_files(output_files, final_output_path, owner, repo_name)

                    if combined_markdown_path:
                        html_content = convert_markdown_to_html(combined_markdown_path)
                        if html_content:
                            return render(request, 'mcp_manager/documentation_display.html', {
                                'documentation': html_content
                            })
                        else:
                            error = "Failed to convert combined Markdown to HTML."
                            return render(request, 'mcp_manager/documentation_interface.html', {'error': error})
                    else:
                        error = "Failed to combine the documentation files."
                        return render(request, 'mcp_manager/documentation_interface.html', {'error': error})
                else:
                    error = "Invalid GitHub repository URL."
                    return render(request, 'mcp_manager/documentation_interface.html', {'error': error})

            except ValueError as e:
                error = str(e)
                return render(request, 'mcp_manager/documentation_interface.html', {'error': error})

    return render(request, 'mcp_manager/documentation_interface.html')



# will be deleting the following as these feel unnecessary
# # 
# def mcp_interface(request):
#     # Keep your existing mcp_interface for manual command testing if needed
#     return render(request, 'mcp_manager/mcp_interface.html')

# def run_mcp_command(request):
#     # Keep your existing run_mcp_command for manual command testing if needed
#     output = ""
#     error = ""
#     if request.method == 'POST':
#         command_text = request.POST.get('command', 'get_issue')
#         owner = request.POST.get('owner', '')
#         repo = request.POST.get('repo', '')
#         issue_number_str = request.POST.get('issue_number', '')
#         issue_number = issue_number_str if issue_number_str else None

#         if GITHUB_TOKEN:
#             try:
#                 mcpcurl_path = os.path.join(os.getcwd(), 'mcpcurl')  # Assuming mcpcurl is in the project root

#                 command_list = [mcpcurl_path, '--stdio-server-cmd',
#                                f'/usr/local/bin/github-mcp-server --toolsets repos,issues,pull_requests,code_security stdio',
#                                'tools', command_text]
#                 if command_text == 'get_issue' and owner and repo and issue_number:
#                     command_list.extend(['--owner', owner, '--repo', repo, '--issue_number', issue_number])
#                 elif command_text == 'list_issues' and owner and repo:
#                     command_list.extend(['--owner', owner, '--repo', repo])

#                 env = {'GITHUB_PERSONAL_ACCESS_TOKEN': GITHUB_TOKEN}
#                 process = subprocess.Popen(command_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
#                 stdout, stderr = process.communicate(timeout=20)
#                 process.wait()
#                 output = stdout.strip()
#                 error = stderr.strip()

#             except FileNotFoundError as e:
#                 error = f"Error: mcpcurl not found at {os.path.join(os.getcwd(), 'mcpcurl')}. Ensure it's in your project root. {e}"
#             except subprocess.TimeoutExpired:
#                 error = "Error: Timeout communicating with mcpcurl."
#             except Exception as e:
#                 error = f"An unexpected error occurred: {e}"
#         else:
#             error = "Error: GITHUB_PERSONAL_ACCESS_TOKEN is not set in Django settings."

#     return render(request, 'mcp_manager/mcp_interface.html', {'output': output, 'error': error})