import subprocess
import json
import os
import threading
import markdown
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from .crews.crew import build_crew
from . import jobs




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

# Emitted before each report so the frontend can split sections reliably.
# Agents vary their heading levels and add their own "---" rules, so neither
# <h1> nor <hr> is a dependable boundary on its own. An HTML comment survives
# markdown conversion verbatim and renders nothing.
SECTION_MARKER = "SECTION:"


# The utility function that combines multiple markdown files
def combine_markdown_files(file_paths, output_path, owner, repo_name, section_keys=None):
    combined_content = f"# Summary for {owner}/{repo_name}\n\n"
    for index, file_path in enumerate(file_paths):
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                markdown_content = ""
                # The agent wraps output in a fence whose info string varies
                # ("```markdown", plain "```", ...), so match any opening fence.
                if lines and lines[0].strip().startswith("```") and len(lines) > 1 and lines[-1].strip() == "```":
                    markdown_content = "".join(lines[1:-1]).strip()
                else:
                    markdown_content = "".join(lines).strip()
                key = section_keys[index] if section_keys and index < len(section_keys) else str(index)
                combined_content += f"\n\n<!--{SECTION_MARKER}{key}-->\n\n" + markdown_content
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

def _normalize_list_indentation(markdown_text):
    """Double leading indentation so nested lists survive conversion.

    The agents emit file trees indented two spaces per level, but
    Python-Markdown needs four to treat an item as nested. Without this the
    whole tree collapses to a single flat level.
    """
    lines = []
    for line in markdown_text.splitlines():
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        lines.append(" " * (indent * 2) + stripped if stripped else line)
    return "\n".join(lines)


# The utility function to change markdown to HTML
def convert_markdown_to_html(markdown_file_path):
    try:
        with open(markdown_file_path, "r") as f:
            markdown_text = _normalize_list_indentation(f.read())
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


def _run_crew_job(job_id, owner, repo_name):
    try:
        if not GOOGLE_API_KEY:
            jobs.fail_job(job_id, "GOOGLE_API_KEY is not set in Django settings.")
            return

        callbacks = {
            "structure": lambda output: jobs.mark_step_done(job_id, "structure"),
            "issues": lambda output: jobs.mark_step_done(job_id, "issues"),
            "pulls": lambda output: jobs.mark_step_done(job_id, "pulls"),
            "branches": lambda output: jobs.mark_step_done(job_id, "branches"),
        }
        crew = build_crew(owner, repo_name, callbacks=callbacks)
        crew.kickoff()

        generated_docs_dir = os.path.join(settings.BASE_DIR, "generated_docs")
        output_files = [
            os.path.join(generated_docs_dir, "repo_structure.md"),
            os.path.join(generated_docs_dir, "report_issues.md"),
            os.path.join(generated_docs_dir, "pull_requests.md"),
            os.path.join(generated_docs_dir, "branches.md"),
        ]
        final_output_path = os.path.join(generated_docs_dir, "summary.md")
        combined_markdown_path = combine_markdown_files(
            output_files, final_output_path, owner, repo_name,
            section_keys=["structure", "issues", "pulls", "branches"],
        )

        if not combined_markdown_path:
            jobs.fail_job(job_id, "Failed to combine the documentation files.")
            return

        html_content = convert_markdown_to_html(combined_markdown_path)
        if not html_content:
            jobs.fail_job(job_id, "Failed to convert combined Markdown to HTML.")
            return

        jobs.finish_job(job_id, html_content)
    except Exception as e:
        jobs.fail_job(job_id, str(e))


def generate_documentation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    repo_url = request.POST.get('repo_url', '')
    if not repo_url:
        return JsonResponse({'error': 'repo_url is required'}, status=400)

    try:
        owner, repo_name = extract_owner_repo(repo_url)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if not owner or not repo_name:
        return JsonResponse({'error': 'Invalid GitHub repository URL.'}, status=400)

    job_id = jobs.create_job(owner, repo_name)
    threading.Thread(target=_run_crew_job, args=(job_id, owner, repo_name), daemon=True).start()
    return JsonResponse({'job_id': job_id})


def job_status(request, job_id):
    job = jobs.get_job(job_id)
    if job is None:
        return JsonResponse({'error': 'Job not found.'}, status=404)
    return JsonResponse(job)



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