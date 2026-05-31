import requests
from config import config

BASE_URL = "https://api.todoist.com/api/v1"
REQUEST_TIMEOUT = 15


class TodoistAPIError(Exception):
    pass


def _log(message):
    print(f"[todoist] {message}", flush=True)


def _headers():
    return {"Authorization": f"Bearer {config.TODOIST_API_KEY}"}


def _request(method, path, **kwargs):
    url = f"{BASE_URL}{path}"
    try:
        response = requests.request(
            method,
            url,
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout as exc:
        raise TodoistAPIError("Todoist request timed out. Please try again.") from exc
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise TodoistAPIError(f"Todoist API error ({status}). Please try again.") from exc
    except requests.exceptions.RequestException as exc:
        raise TodoistAPIError("Could not reach Todoist. Check your internet connection.") from exc


def get_tasks():
    _log("Fetching active tasks")
    r = _request("GET", "/tasks")

    data = r.json()

    # 🔥 Handle your response shape
    if isinstance(data, dict) and "results" in data:
        return data["results"]

    return data

def delete_task(task_id):
    _log(f"Deleting task {task_id}")
    _request("DELETE", f"/tasks/{task_id}")

# todoist_module.py

from datetime import datetime

def create_task(content):
    now = datetime.now()
    today_date = now.date().isoformat()
    # Format for due_datetime: YYYY-MM-DDTHH:MM:SSZ (UTC) or YYYY-MM-DDTHH:MM:SS (Local)
    # Todoist API accepts ISO format
    now_datetime = now.isoformat()

    payload = {
        "content": content,
        "due_date": today_date,
        "due_datetime": now_datetime
    }

    r = _request("POST", "/tasks", json=payload)

    try:
        data = r.json()
        _log(f"Created task: {content}")
        return data
    except Exception:
        _log(f"Failed to parse response while creating task: {content}")
        return None
    

def get_relevant_tasks():
    tasks = get_tasks()

    ai_tasks = []
    mem_add = []
    mem_rem = []
    mem_show = []
    for t in tasks:
        c = t["content"]

        if "@ai" in c:
            ai_tasks.append(t)

        elif "@memadd" in c:
            mem_add.append(t)

        elif "@memrem" in c:
            mem_rem.append(t)

        elif "@mem" in c:
            mem_show.append(t)

    return ai_tasks, mem_add, mem_rem, mem_show


def create_tasks_bulk(steps):
    ids = []

    _log(f"Creating {len(steps)} subtasks")
    for step in steps:
        task = create_task(step)

        if task and "id" in task:
            ids.append(task["id"])
        else:
            _log(f"Failed to create task: {step}")

    return ids


def delete_all_active_tasks():
    tasks = get_tasks()
    deleted = 0

    for task in tasks:
        delete_task(task["id"])
        deleted += 1

    _log(f"Deleted {deleted} active task(s)")
    return deleted
def get_active_task_ids():
    tasks = get_tasks()
    return {t["id"] for t in tasks}
