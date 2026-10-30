from typing import List
from models.task import Task


class CLIView:
    """Handles I/O operations for CLI."""

    @staticmethod
    def get_login_credentials() -> tuple[str, str]:
        print("\n--- LOGIN ---")
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        return username, password

    @staticmethod
    def get_registration_input() -> tuple[str, str, str]:
        print("\n--- REGISTER NEW USER ---")
        username = input("Enter new username: ").strip()
        password = input("Enter password: ").strip()
        confirm = input("Confirm password: ").strip()
        return username, password, confirm

    @staticmethod
    def get_add_task_input() -> tuple[str, str, str, str]:
        print("\n--- ADD TASK ---")
        assignee = input("Enter assignee: ").strip()
        title = input("Enter task title: ").strip()
        desc = input("Enter task description: ").strip()
        due = input("Enter due date (25 Oct 2026): ").strip()
        return assignee, title, desc, due

    @staticmethod
    def display_tasks(
        tasks: List[Task], header: str = "ALL TASKS"
    ) -> None:
        print(f"\n--- {header} ---")
        if not tasks:
            print("No tasks found.")
            return

        for task in tasks:
            print("-" * 35)
            print(f"Task ID:          {task.task_id}")
            print(f"Task:             {task.title}")
            print(f"Assigned to:      {task.username}")
            print(f"Date assigned:    {task.assigned_date}")
            print(f"Due date:         {task.due_date}")
            print(f"Task Complete?    {task.completed_str}")
            print(f"Task Description:\n {task.description}")

    @staticmethod
    def prompt_my_task_action() -> tuple[int, str]:
        try:
            prompt = "\nEnter Task ID (-1 for menu): "
            task_id = int(input(prompt).strip())
            if task_id == -1:
                return -1, ""

            print("\nOptions:")
            print("1. Mark task complete")
            print("2. Edit task details")
            action = input("Select option (1-2): ").strip()
            return task_id, action
        except ValueError:
            return -2, ""

    @staticmethod
    def get_edit_task_input() -> tuple[str, str]:
        new_u = input("New assignee (Enter to keep): ").strip()
        new_d = input("New due date (Enter to keep): ").strip()
        return new_u, new_d

    @staticmethod
    def prompt_delete_task() -> int:
        print("\n--- DELETE TASK ---")
        try:
            return int(input("Task ID to delete: ").strip())
        except ValueError:
            return -1

    @staticmethod
    def main_menu(is_admin: bool) -> str:
        print("\n===================================")
        print("             MAIN MENU             ")
        print("===================================")
        print("r  - Register User")
        print("a  - Add Task")
        print("va - View All Tasks")
        print("vm - View My Tasks")
        if is_admin:
            print("vc - View Completed Tasks")
            print("d  - Delete Task")
            print("ds - Display Statistics")
            print("gr - Generate Reports")
        print("e  - Exit")
        return input("Select option: ").strip().lower()

    @staticmethod
    def show_message(message: str) -> None:
        print(message)
