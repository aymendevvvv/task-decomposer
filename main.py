# main.py

import tkinter as tk
from tkinter import ttk

from ai.factory import get_ai_provider
from todoist_module import (
    get_active_task_ids,
    get_relevant_tasks,
    delete_task,
    create_task,
)
from memory_module import add_memory, remove_memory, get_memory_tasks
from config import config


class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Progress")

        # ✅ NORMAL WINDOW (movable)
        self.root.geometry("800x300")  # clean wide layout
        self.root.minsize(600, 200)

        # Dark background
        self.root.configure(bg="#111")

        # Container
        self.container = tk.Frame(root, bg="#111")
        self.container.pack(fill="both", expand=True, padx=30, pady=30)

        # Task label
        self.label = tk.Label(
            self.container,
            text="Waiting for task...",
            font=("Arial", 24),
            fg="white",
            bg="#111"
        )
        self.label.pack(pady=20)

        # Progress bar style (better visibility)
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Horizontal.TProgressbar",
            thickness=20
        )

        # Progress bar (full width)
        self.progress = ttk.Progressbar(
            self.container,
            style="Custom.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate"
        )
        self.progress.pack(fill="x", expand=True, pady=20)

        self.total_steps = 0
        self.task_ids = set()

        self.ai = get_ai_provider()

        self.poll()

    def poll(self):
        ai_tasks, mem_add, mem_rem, mem_show = get_relevant_tasks()

        # --- Memory Add ---
        for t in mem_add:
            add_memory(t["content"])
            delete_task(t["id"])

        # --- Memory Remove ---
        for t in mem_rem:
            parts = t["content"].split()
            if len(parts) > 1:
                remove_memory(parts[1])
            delete_task(t["id"])

        # --- Memory Show ---
        for t in mem_show:
            mem_items = get_memory_tasks()
            for item in mem_items:
                create_task(item)
            delete_task(t["id"])

        # --- AI Task ---
        if ai_tasks:
            task = ai_tasks[0]
            content = task["content"].replace("@ai", "").strip()

            steps = self.ai.generate_steps(content)

            delete_task(task["id"])

            created_ids = set()
            for step in steps:
                t = create_task(step)
                if t and "id" in t:
                    created_ids.add(t["id"])

            self.task_ids = created_ids
            self.total_steps = len(self.task_ids)

            self.label.config(text=f"Task: {content}")

        self.update_progress()

        self.root.after(config.POLL_INTERVAL * 1000, self.poll)

    def update_progress(self):
        if not self.task_ids:
            return

        active_ids = get_active_task_ids()

        remaining = self.task_ids.intersection(active_ids)
        done = self.total_steps - len(remaining)

        progress = done / self.total_steps if self.total_steps else 0
        self.progress["value"] = progress * 100


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()