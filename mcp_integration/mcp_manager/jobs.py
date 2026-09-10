import threading
import uuid

_jobs = {}
_lock = threading.Lock()

STEPS = [
    {"key": "structure", "label": "Repository Structure"},
    {"key": "issues", "label": "Issue Analysis"},
    {"key": "pulls", "label": "Pull Requests"},
    {"key": "branches", "label": "Branches"},
]


def create_job(owner, repo):
    job_id = uuid.uuid4().hex
    steps = [{"key": s["key"], "label": s["label"], "status": "pending"} for s in STEPS]
    if steps:
        steps[0]["status"] = "running"
    with _lock:
        _jobs[job_id] = {
            "status": "running",
            "owner": owner,
            "repo": repo,
            "steps": steps,
            "error": None,
            "result_html": None,
        }
    return job_id


def get_job(job_id):
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def mark_step_done(job_id, step_key):
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        for step in job["steps"]:
            if step["key"] == step_key:
                step["status"] = "done"
            elif step["status"] == "pending":
                # Process.sequential runs one task at a time, so the next
                # pending step is now the one actively running.
                step["status"] = "running"
                break


def finish_job(job_id, html):
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job["status"] = "done"
        job["result_html"] = html


def fail_job(job_id, error_message):
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job["status"] = "error"
        job["error"] = error_message
