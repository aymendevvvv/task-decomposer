import requests
from config import config

BASE_URL = "https://api.todoist.com/api/v1"


def _headers():
    return {"Authorization": f"Bearer {config.TODOIST_API_KEY}"}


def get_tasks():
    r = requests.get(f"{BASE_URL}/tasks", headers=_headers())
    r.raise_for_status()

    data = r.json()

    # 🔥 Handle your response shape
    if isinstance(data, dict) and "results" in data:
        return data["results"]

    return data

def delete_task(task_id):
    requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=_headers())

# todoist_module.py

from datetime import date

def create_task(content):
    today = date.today().isoformat()

    payload = {
        "content": content,
        "due": {
            "date": today
        }
    }

    r = requests.post(
        f"{BASE_URL}/tasks",
        headers=_headers(),
        json=payload
    )

    try:
        return r.json()
    except:
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

    for step in steps:
        task = create_task(step)

        if task and "id" in task:
            ids.append(task["id"])
        else:
            print("⚠️ Failed to create task:", step)

    return ids
def get_active_task_ids():
    tasks = get_tasks()
    return {t["id"] for t in tasks}
