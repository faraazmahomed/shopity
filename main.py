import os
from datetime import datetime
from typing import Optional
from models import Task, User
from storage import FileHandler


class TaskManagementCLI:
    """CLI Menu Driver mapping user workflows."""

    def __init__(self) -> None:
        FileHandler.ensure_files_exist()
        self.current_user: Optional[User] = None

    def login(self) -> bool:
        """UC-1: Authenticate / Login"""
        print("\n--- LOGIN ---")
        users = FileHandler.load_users()

        while True:
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()

            if (
                username in users
                and users[username].password == password
            ):
                self.current_user = users[username]
                print(f"\nLogin successful! Welcome, {username}.")
                return True

            print("Invalid credentials. Please try again.\n")

    def register_user(self) -> None:
        """UC-7: Register User (Admin Only)"""
        if not self.current_user or not self.current_user.is_admin:
            print("Access denied. Admin privileges required.")
            return

        print("\n--- REGISTER NEW USER ---")
        users = FileHandler.load_users()
        new_username = input("Enter new username: ").strip()

        if new_username in users:
            print("Error: Username already exists.")
            return

        password = input("Enter password: ").strip()
        confirm_password = input("Confirm password: ").strip()

        if password != confirm_password:
            print("Error: Passwords do not match.")
            return

        new_user = User(new_username, password)
        FileHandler.save_user(new_user)
        print(f"User '{new_username}' registered successfully!")

    def add_task(self) -> None:
        """UC-2: Add Task"""
        print("\n--- ADD TASK ---")
        users = FileHandler.load_users()
        assignee = input("Enter assignee username: ").strip()

        if assignee not in users:
            print("Error: User does not exist.")
            return

        title = input("Enter task title: ").strip()
        desc = input("Enter task description: ").strip()
        due_date = input("Enter due date (e.g., 25 Oct 2026): ").strip()
        assigned_date = datetime.now().strftime("%d %b %Y")

        new_task = Task(
            assignee, title, desc, assigned_date, due_date
        )
        tasks = FileHandler.load_tasks()
        tasks.append(new_task)
        FileHandler.save_tasks(tasks)
        print("Task added successfully!")

    def view_all_tasks(self) -> None:
        """UC-3: View All Tasks"""
        print("\n--- ALL TASKS ---")
        tasks = FileHandler.load_tasks()
        if not tasks:
            print("No tasks found.")
            return

        for task in tasks:
            print("-----------------------------------")
            print(task)

    def view_my_tasks(self) -> None:
        """UC-4: View My Tasks with UC-5 & UC-6 options."""
        print("\n--- MY TASKS ---")
        tasks = FileHandler.load_tasks()
        my_tasks = [
            t
            for t in tasks
            if t.username == self.current_user.username
        ]

        if not my_tasks:
            print("You have no assigned tasks.")
            return

        for task in my_tasks:
            print("-----------------------------------")
            print(task)

        print("-----------------------------------")
        try:
            prompt = (
                "Enter Task ID to select a task, "
                "or -1 to return to main menu: "
            )
            choice = int(input(prompt))
            if choice == -1:
                return

            sel_task = next(
                (t for t in tasks if t.task_id == choice), None
            )
            if (
                not sel_task
                or sel_task.username != self.current_user.username
            ):
                print("Invalid Task ID or not authorized.")
                return

            print("\nOptions:")
            print("1. Mark task as complete (UC-5)")
            print("2. Edit task details (UC-6)")
            action = input("Select an option (1-2): ").strip()

            if action == "1":
                sel_task.mark_complete()
                FileHandler.save_tasks(tasks)
                print("Task marked as complete!")

            elif action == "2":
                if sel_task.completed:
                    print("Error: Completed tasks cannot be edited.")
                    return

                new_user = input(
                    "Enter new assignee username (or Enter to keep): "
                ).strip()
                new_due = input(
                    "Enter new due date (or Enter to keep): "
                ).strip()

                sel_task.edit_details(
                    new_username=new_user if new_user else None,
                    new_due_date=new_due if new_due else None,
                )
                FileHandler.save_tasks(tasks)
                print("Task updated successfully!")

        except ValueError as e:
            print(f"Invalid input: {e}")

    def view_completed_tasks(self) -> None:
        """UC-8: View Completed Tasks (Admin Only)"""
        if not self.current_user.is_admin:
            print("Access denied.")
            return

        print("\n--- COMPLETED TASKS ---")
        tasks = FileHandler.load_tasks()
        completed = [t for t in tasks if t.completed]

        if not completed:
            print("No completed tasks.")
            return

        for task in completed:
            print("-----------------------------------")
            print(task)

    def delete_task(self) -> None:
        """UC-9: Delete Task (Admin Only)"""
        if not self.current_user.is_admin:
            print("Access denied.")
            return

        print("\n--- DELETE TASK ---")
        tasks = FileHandler.load_tasks()
        try:
            task_id = int(input("Enter Task ID to delete: "))
            to_remove = next(
                (t for t in tasks if t.task_id == task_id), None
            )

            if not to_remove:
                print("Task ID not found.")
                return

            tasks.remove(to_remove)
            FileHandler.save_tasks(tasks)
            print("Task deleted successfully!")
        except ValueError:
            print("Invalid Task ID.")

    def display_statistics(self) -> None:
        """UC-10: Display Statistics (Includes UC-11)"""
        if not self.current_user.is_admin:
            print("Access denied.")
            return

        if not os.path.exists(
            FileHandler.TASK_OVERVIEW_FILE
        ) or not os.path.exists(FileHandler.USER_OVERVIEW_FILE):
            print("Generating reports...")
            FileHandler.generate_reports()

        print("\n--- SYSTEM STATISTICS ---")
        print("\n[Task Overview]")
        with open(FileHandler.TASK_OVERVIEW_FILE, "r") as f:
            print(f.read())

        print("\n[User Overview]")
        with open(FileHandler.USER_OVERVIEW_FILE, "r") as f:
            print(f.read())

    def run(self) -> None:
        """Main Program Controller Loop."""
        if not self.login():
            return

        while True:
            print("\n===================================")
            print("             MAIN MENU             ")
            print("===================================")
            print("r  - Register User (UC-7)")
            print("a  - Add Task (UC-2)")
            print("va - View All Tasks (UC-3)")
            print("vm - View My Tasks (UC-4 / UC-5 / UC-6)")
            if self.current_user.is_admin:
                print("vc - View Completed Tasks (UC-8)")
                print("d  - Delete Task (UC-9)")
                print("ds - Display Statistics (UC-10)")
                print("gr - Generate Reports (UC-11)")
            print("e  - Exit")

            menu_choice = input("Select an option: ").strip().lower()

            if menu_choice == "r" and self.current_user.is_admin:
                self.register_user()
            elif menu_choice == "a":
                self.add_task()
            elif menu_choice == "va":
                self.view_all_tasks()
            elif menu_choice == "vm":
                self.view_my_tasks()
            elif menu_choice == "vc" and self.current_user.is_admin:
                self.view_completed_tasks()
            elif menu_choice == "d" and self.current_user.is_admin:
                self.delete_task()
            elif menu_choice == "ds" and self.current_user.is_admin:
                self.display_statistics()
            elif menu_choice == "gr" and self.current_user.is_admin:
                FileHandler.generate_reports()
                print("Reports generated successfully!")
            elif menu_choice == "e":
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    app = TaskManagementCLI()
    app.run()

    