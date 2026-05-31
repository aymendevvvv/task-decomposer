# main.py

import tkinter as tk
from tkinter import ttk
import traceback

from ai.factory import get_ai_provider
from todoist_module import (
    TodoistAPIError,
    get_active_task_ids,
    get_relevant_tasks,
    delete_task,
    create_task,
    create_tasks_bulk,
    delete_all_active_tasks,
)
from memory_module import add_memory, remove_memory, get_memory_tasks
from config import config


import time


def _log(message):
    print(f"[app] {message}", flush=True)


class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Task Decomposer")
        self.root.geometry("800x400")
        self.root.minsize(700, 350)
        self.root.configure(bg="#1e1e1e")

        # Custom Styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Progress Bar Style
        self.style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor="#333",
            background="#4CAF50",
            bordercolor="#1e1e1e",
            lightcolor="#4CAF50",
            darkcolor="#4CAF50",
            thickness=15
        )

        # Main Layout
        self.main_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Top Panel
        self.top_panel = tk.Frame(self.main_frame, bg="#2d2d2d", height=80)
        self.top_panel.pack(fill="x", pady=(0, 20))
        self.top_panel.pack_propagate(False)

        self.title_label = tk.Label(
            self.top_panel,
            text="TASK DECOMPOSER",
            font=("Segoe UI", 12, "bold"),
            fg="#888",
            bg="#2d2d2d"
        )
        self.title_label.pack(side="left", padx=20)

        self.stopwatch_label = tk.Label(
            self.top_panel,
            text="00:00:00",
            font=("Consolas", 24, "bold"),
            fg="#4CAF50",
            bg="#2d2d2d"
        )
        self.stopwatch_label.pack(side="right", padx=20)

        # Task Display
        self.task_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.task_frame.pack(fill="x", pady=10)

        self.label = tk.Label(
            self.task_frame,
            text="Waiting for task...",
            font=("Segoe UI", 20),
            fg="#ffffff",
            bg="#1e1e1e",
            wraplength=700
        )
        self.label.pack(pady=10)

        self.error_label = tk.Label(
            self.task_frame,
            text="",
            font=("Segoe UI", 11),
            fg="#ff7b72",
            bg="#1e1e1e",
            wraplength=700,
            justify="center",
        )
        self.error_label.pack(pady=(0, 8))

        # Start Button
        self.start_btn = tk.Button(
            self.main_frame,
            text="START TASK",
            font=("Segoe UI", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="flat",
            padx=30,
            pady=10,
            command=self.start_task
        )
        self.start_btn.pack(pady=10)
        self.start_btn.pack_forget()  # Hide initially

        # Progress Section
        self.progress_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.progress_frame.pack(fill="x", side="bottom", pady=20)

        self.progress_label = tk.Label(
            self.progress_frame,
            text="0%",
            font=("Segoe UI", 10, "bold"),
            fg="#888",
            bg="#1e1e1e"
        )
        self.progress_label.pack(anchor="e")

        self.progress = ttk.Progressbar(
            self.progress_frame,
            style="Modern.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate"
        )
        self.progress.pack(fill="x", expand=True)

        # State
        self.total_steps = 0
        self.task_ids = set()
        self.ai = get_ai_provider()
        self.start_time = None
        self.is_running = False

        self.poll()

    def start_task(self):
        try:
            self.clear_error()
            # Fetch current active tasks from Todoist right now to account for any manual changes
            _log("Start button clicked; confirming current Todoist task count")
            current_active_ids = get_active_task_ids()
            
            if not current_active_ids:
                _log("No active tasks found at start time")
                self.show_error("No active Todoist tasks found to start.")
                return
                
            self.task_ids = set(current_active_ids)
            self.total_steps = len(self.task_ids)
            self.start_time = time.time()
            self.is_running = True
            _log(f"Tracking {self.total_steps} task(s) for progress")
            self.start_btn.pack_forget()
            self.update_timer()
            self.update_progress()
        except Exception as exc:
            self.handle_error(exc, "Could not start task tracking.")

    def update_timer(self):
        if self.is_running and self.start_time:
            elapsed = int(time.time() - self.start_time)
            hours, rem = divmod(elapsed, 3600)
            minutes, seconds = divmod(rem, 60)
            self.stopwatch_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)

    def reset_state(self):
        """Resets the application state to prepare for a new task."""
        _log("Resetting local app state")
        self.is_running = False
        self.start_time = None
        self.total_steps = 0
        self.task_ids = set()
        self.stopwatch_label.config(text="00:00:00", fg="#4CAF50")
        self.progress["value"] = 0
        self.progress_label.config(text="0%")
        self.start_btn.pack_forget()

    def clear_error(self):
        self.error_label.config(text="")

    def show_error(self, message):
        _log(f"ERROR: {message}")
        self.error_label.config(text=message)

    def handle_error(self, exc, fallback_message):
        traceback.print_exc()
        if isinstance(exc, TodoistAPIError):
            message = str(exc)
        else:
            message = f"{fallback_message} {exc}"
        self.show_error(message)

    def poll(self):
        try:
            ai_tasks, mem_add, mem_rem, mem_show = get_relevant_tasks()

            # Clear stale errors after a successful poll.
            self.clear_error()

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

            if ai_tasks:
                task = ai_tasks[0]
                content = task["content"].replace("@ai", "").strip()
                _log(f"Received new @ai task: {content}")
                
                # 1. Delete all existing active tasks first, including the @ai trigger task.
                deleted_count = delete_all_active_tasks()
                _log(f"Cleared {deleted_count} existing task(s) before creating new subtasks")
                
                # 2. Reset local UI and state
                self.reset_state()
                
                # 3. Summarize and show receive status
                summary = self.ai.summarize_task(content)
                _log(f"Task summary: {summary}")
                self.label.config(text=f"Task: {summary}")
                
                # 4. Generate new steps
                steps = self.ai.generate_steps(content)
                _log(f"Generated {len(steps)} suggested subtask(s)")
                
                # 5. Create subtasks immediately in Todoist.
                created_ids = create_tasks_bulk(steps)
                _log(f"Created {len(created_ids)} subtask(s) in Todoist")

                # The button only confirms the final count after manual edits in Todoist.
                self.start_btn.pack(pady=10)
                if created_ids:
                    self.label.config(text=f"Task: {summary}")
                else:
                    self.label.config(text="Task received, but subtask creation failed")
                    self.show_error("Todoist did not accept the generated subtasks.")

            if self.is_running:
                self.update_progress()
        except Exception as exc:
            self.handle_error(exc, "Background sync failed.")
        finally:
            self.root.after(config.POLL_INTERVAL * 1000, self.poll)

    def update_progress(self):
        try:
            if not self.task_ids:
                return

            active_ids = get_active_task_ids()
            remaining = self.task_ids.intersection(active_ids)
            
            if not remaining and self.is_running:
                self.is_running = False
                self.label.config(text="All tasks completed!")
                self.task_ids = set()
                self.total_steps = 0
                return

            done = self.total_steps - len(remaining)
            progress = (done / self.total_steps) * 100 if self.total_steps else 0
            self.progress["value"] = progress
            self.progress_label.config(text=f"{int(progress)}%")
        except Exception as exc:
            self.handle_error(exc, "Could not update progress.")



if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()
