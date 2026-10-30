from datetime import datetime
from typing import Optional

from models.report import ReportGenerator
from models.storage import FileHandler
from models.task import Task
from models.user import User
from views.cli_view import CLIView


class TaskController:
    """Controls application flow and business execution."""

    def __init__(self):
        FileHandler.ensure_files_exist()
        self.view = CLIView()
        self.current_user: Optional[User] = None

    def login(self) -> bool:
        users = FileHandler.load_users()
        while True:
            u, p = self.view.get_login_credentials()
            if u in users and users[u].authenticate(p):
                self.current_user = users[u]
                self.view.show_message(
                    f"\nLogin successful! Welcome, {u}."
                )
                return True
            self.view.show_message(
                "Invalid credentials. Try again."
            )

    def register_user(self) -> None:
        if not self.current_user or not self.current_user.is_admin:
            self.view.show_message("Access denied. Admin required.")
            return

        users = FileHandler.load_users()
        u, p, c = self.view.get_registration_input()

        if u in users:
            self.view.show_message("Error: Username exists.")
            return
        if p != c:
            self.view.show_message("Error: Passwords match fail.")
            return

        new_user = User(u, p)
        FileHandler.save_user(new_user)
        self.view.show_message(
            f"User '{u}' registered successfully!"
        )

    def add_task(self) -> None:
        users = FileHandler.load_users()
        a, t, d, due = self.view.get_add_task_input()

        if a not in users:
            self.view.show_message("Error: Assignee not found.")
            return

        assigned_date = datetime.now().strftime("%d %b %Y")
        new_task = Task(a, t, d, assigned_date, due)

        tasks = FileHandler.load_tasks()
        tasks.append(new_task)
        FileHandler.save_tasks(tasks)
        self.view.show_message("Task added successfully!")

    def view_all_tasks(self) -> None:
        tasks = FileHandler.load_tasks()
        self.view.display_tasks(tasks, "ALL TASKS")

    def view_my_tasks(self) -> None:
        tasks = FileHandler.load_tasks()
        my_t = [
            t for t in tasks
            if t.username == self.current_user.username
        ]
        self.view.display_tasks(
            my_t, f"MY TASKS ({self.current_user.username})"
        )

        if not my_t:
            return

        task_id, act = self.view.prompt_my_task_action()
        if task_id in (-1, -2):
            if task_id == -2:
                self.view.show_message("Invalid Task ID.")
            return

        tgt = next((t for t in tasks if t.task_id == task_id), None)
        if (
            not tgt
            or tgt.username != self.current_user.username
        ):
            self.view.show_message("Unauthorized selection.")
            return

        if act == "1":
            tgt.mark_complete()
            FileHandler.save_tasks(tasks)
            self.view.show_message("Task marked complete!")
        elif act == "2":
            if tgt.completed:
                self.view.show_message(
                    "Error: Completed task cannot edit."
                )
                return
            new_u, new_d = self.view.get_edit_task_input()
            try:
                tgt.edit_details(
                    new_username=new_u if new_u else None,
                    new_due_date=new_d if new_d else None,
                )
                FileHandler.save_tasks(tasks)
                self.view.show_message("Task updated!")
            except ValueError as e:
                self.view.show_message(str(e))

    def view_completed_tasks(self) -> None:
        if not self.current_user.is_admin:
            self.view.show_message("Access denied.")
            return
        tasks = FileHandler.load_tasks()
        completed = [t for t in tasks if t.completed]
        self.view.display_tasks(completed, "COMPLETED TASKS")

    def delete_task(self) -> None:
        if not self.current_user.is_admin:
            self.view.show_message("Access denied.")
            return

        task_id = self.view.prompt_delete_task()
        tasks = FileHandler.load_tasks()
        tgt = next((t for t in tasks if t.task_id == task_id), None)

        if not tgt:
            self.view.show_message("Task ID not found.")
            return

        tasks.remove(tgt)
        FileHandler.save_tasks(tasks)
        self.view.show_message("Task deleted successfully!")

    def generate_reports(self) -> None:
        if not self.current_user.is_admin:
            self.view.show_message("Access denied.")
            return

        tasks = FileHandler.load_tasks()
        users = FileHandler.load_users()

        t_rep = ReportGenerator.generate_task_report(tasks)
        u_rep = ReportGenerator.generate_user_report(users, tasks)

        FileHandler.write_report_files(t_rep, u_rep)
        self.view.show_message("Reports generated successfully!")

    def display_statistics(self) -> None:
        if not self.current_user.is_admin:
            self.view.show_message("Access denied.")
            return

        t_rep, u_rep = FileHandler.read_reports()
        if not t_rep or not u_rep:
            self.generate_reports()
            t_rep, u_rep = FileHandler.read_reports()

        self.view.show_message("\n--- SYSTEM STATISTICS ---")
        self.view.show_message(t_rep)
        self.view.show_message(u_rep)

    def run(self) -> None:
        if not self.login():
            return

        while True:
            choice = self.view.main_menu(
                self.current_user.is_admin
            )

            if choice == "r" and self.current_user.is_admin:
                self.register_user()
            elif choice == "a":
                self.add_task()
            elif choice == "va":
                self.view_all_tasks()
            elif choice == "vm":
                self.view_my_tasks()
            elif choice == "vc" and self.current_user.is_admin:
                self.view_completed_tasks()
            elif choice == "d" and self.current_user.is_admin:
                self.delete_task()
            elif choice == "ds" and self.current_user.is_admin:
                self.display_statistics()
            elif choice == "gr" and self.current_user.is_admin:
                self.generate_reports()
            elif choice == "e":
                self.view.show_message("Goodbye!")
                break
            else:
                self.view.show_message("Invalid option.")
