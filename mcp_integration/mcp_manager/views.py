import subprocess
import json
import os
import markdown
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from langchain_openai import ChatOpenAI

# Task 11: Import the generate_documentation function



GITHUB_TOKEN = getattr(settings, 'GITHUB_PERSONAL_ACCESS_TOKEN', None)
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', None)

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


# Task 4: Write the function to render the documentation interface
def documentation_interface(request):
    return render(request, 'mcp_manager/documentation_interface.html')


# Task 11: Define the generate_documentation() function











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