import threading
import tkinter as tk
from tkinter import ttk
import time
import random
from queue import Queue, Empty

class TaskManagerGUI:
    def __init__(self, master, task_queue, completed_tasks):
        self.master = master
        self.task_queue = task_queue
        self.completed_tasks = completed_tasks
        master.title("Task Manager")
        master.configure(bg="#2d2d2d")
        # Style configuration
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 12), background="#2d2d2d", foreground="white")
        style.configure("TButton", font=("Arial", 12), background="#4CAF50", foreground="black")
        style.configure("TListbox", font=("Arial", 12), background="#363636", foreground="white")

        # Widgets
        self.label = ttk.Label(master, text="Task Manager", style="TLabel")
        self.label.pack()

        self.entry = ttk.Entry(master, font=("Arial", 12))
        self.entry.pack()

        self.add_button = ttk.Button(master, text="Add Task", command=self.add_task, style="TButton")
        self.add_button.pack()

        self.status_label = ttk.Label(master, text="Status: Idle", style="TLabel")
        self.status_label.pack()

        self.task_listbox = tk.Listbox(master, selectmode=tk.SINGLE, height=10, font=("Arial", 12))
        self.task_listbox.pack()

        self.load_tasks()

    def add_task(self):
        task_description = self.entry.get()
        if task_description:
            self.task_queue.put(task_description)
            self.entry.delete(0, tk.END)  # Clear the entry field
            self.status_label.config(text="Status: Task added")
            self.task_listbox.insert(tk.END, task_description)  # Add the task to the listbox
            self.save_tasks()

    def load_tasks(self):
        try:
            with open("tasks.txt", "r") as file:
                tasks = file.read().splitlines()
                self.task_listbox.delete(0, tk.END)
                for task in tasks:
                    self.task_listbox.insert(tk.END, task)
        except FileNotFoundError:
            pass

    def save_tasks(self):
        with open("tasks.txt", "w") as file:
            tasks = self.task_listbox.get(0, tk.END)
            file.write("\n".join(tasks))

def worker_function(task_queue, shared_data, completed_tasks):
    while not shared_data["exit_flag"]:
        try:
            task_description = task_queue.get(timeout=1)  # Timeout to check exit flag
            print(f"Processing Task: {task_description}")
            # Simulate processing task
            start_time = time.time()
            task_delay = random.uniform(1, 5)
            time.sleep(task_delay)
            end_time = time.time()
            completion_time = end_time - start_time

            print(f"Task '{task_description}' completed in {completion_time:.2f} seconds!")
            completed_tasks.put(task_description)
        except Empty:
            pass

def main():
    task_queue = Queue()
    completed_tasks = Queue()
    shared_data = {
        "exit_flag": False,
    }

    root = tk.Tk()
    root.geometry("400x300")
    app = TaskManagerGUI(root, task_queue, completed_tasks)

    # Start the worker thread
    worker_thread = threading.Thread(target=worker_function, args=(task_queue, shared_data, completed_tasks))
    worker_thread.start()

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, shared_data, worker_thread))
    root.mainloop()

    # Wait for the worker thread to finish before exiting
    worker_thread.join()

def on_closing(root, shared_data, worker_thread):
    shared_data["exit_flag"] = True
    root.destroy()
    # Wait for the worker thread to finish before exiting
    worker_thread.join()

if __name__ == "__main__":
    main()