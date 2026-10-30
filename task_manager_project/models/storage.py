import os
from typing import Dict, List
from models.user import User, AdminUser
from models.task import Task


class FileHandler:
    """Handles persistence operations."""

    USER_FILE = "user.txt"
    TASK_FILE = "tasks.txt"
    TASK_OVERVIEW_FILE = "task_overview.txt"
    USER_OVERVIEW_FILE = "user_overview.txt"

    @classmethod
    def ensure_files_exist(cls) -> None:
        """Ensures storage files exist."""
        if not os.path.exists(cls.USER_FILE):
            with open(cls.USER_FILE, "w") as f:
                f.write("admin, admin\n")

        if not os.path.exists(cls.TASK_FILE):
            open(cls.TASK_FILE, "w").close()

    @classmethod
    def load_users(cls) -> Dict[str, User]:
        """Loads users from file."""
        cls.ensure_files_exist()
        users = {}
        with open(cls.USER_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                parts = [
                    p.strip() for p in line.strip().split(",")
                ]
                if len(parts) >= 2:
                    username, password = parts[0], parts[1]
                    if username == "admin":
                        users[username] = AdminUser(
                            username, password
                        )
                    else:
                        users[username] = User(
                            username, password
                        )
        return users

    @classmethod
    def save_user(cls, user: User) -> None:
        """Appends user to file."""
        with open(cls.USER_FILE, "a") as f:
            f.write(user.to_file_format())

    @classmethod
    def load_tasks(cls) -> List[Task]:
        """Loads tasks from file."""
        cls.ensure_files_exist()
        tasks = []
        with open(cls.TASK_FILE, "r") as f:
            for idx, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                parts = [
                    p.strip() for p in line.strip().split(",")
                ]
                if len(parts) >= 6:
                    completed = parts[5].lower() == "yes"
                    task = Task(
                        username=parts[0],
                        title=parts[1],
                        description=parts[2],
                        assigned_date=parts[3],
                        due_date=parts[4],
                        completed=completed,
                        task_id=idx,
                    )
                    tasks.append(task)
        return tasks

    @classmethod
    def save_tasks(cls, tasks: List[Task]) -> None:
        """Overwrites tasks file."""
        with open(cls.TASK_FILE, "w") as f:
            for task in tasks:
                f.write(task.to_file_format())

    @classmethod
    def write_report_files(
        cls, task_report: str, user_report: str
    ) -> None:
        """Writes report strings to disk."""
        with open(cls.TASK_OVERVIEW_FILE, "w") as f:
            f.write(task_report)

        with open(cls.USER_OVERVIEW_FILE, "w") as f:
            f.write(user_report)

    @classmethod
    def read_reports(cls) -> tuple[str, str]:
        """Reads generated report files."""
        task_data, user_data = "", ""
        if os.path.exists(cls.TASK_OVERVIEW_FILE):
            with open(cls.TASK_OVERVIEW_FILE, "r") as f:
                task_data = f.read()

        if os.path.exists(cls.USER_OVERVIEW_FILE):
            with open(cls.USER_OVERVIEW_FILE, "r") as f:
                user_data = f.read()

        return task_data, user_data
