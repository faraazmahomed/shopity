import os
from typing import Dict, List
from models import AdminUser, Task, User


class FileHandler:
    """Handles line-delimited text storage operations."""

    USER_FILE = "user.txt"
    TASK_FILE = "tasks.txt"
    TASK_OVERVIEW_FILE = "task_overview.txt"
    USER_OVERVIEW_FILE = "user_overview.txt"

    @classmethod
    def ensure_files_exist(cls) -> None:
        """Ensures that user.txt and tasks.txt exist."""
        if not os.path.exists(cls.USER_FILE):
            with open(cls.USER_FILE, "w") as f:
                f.write("admin, admin\n")

        if not os.path.exists(cls.TASK_FILE):
            open(cls.TASK_FILE, "w").close()

    @classmethod
    def load_users(cls) -> Dict[str, User]:
        """Reads user.txt and maps username -> User object."""
        cls.ensure_files_exist()
        users = {}
        with open(cls.USER_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.strip().split(",")]
                if len(parts) >= 2:
                    username, password = parts[0], parts[1]
                    if username == "admin":
                        users[username] = AdminUser(
                            username, password
                        )
                    else:
                        users[username] = User(username, password)
        return users

    @classmethod
    def save_user(cls, user: User) -> None:
        """UC-7: Register User - Appends record to user.txt."""
        with open(cls.USER_FILE, "a") as f:
            f.write(user.to_file_format())

    @classmethod
    def load_tasks(cls) -> List[Task]:
        """Reads tasks.txt and returns list of Task objects."""
        cls.ensure_files_exist()
        tasks = []
        with open(cls.TASK_FILE, "r") as f:
            for idx, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.strip().split(",")]
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
        """Overwrites tasks.txt with updated task records."""
        with open(cls.TASK_FILE, "w") as f:
            for task in tasks:
                f.write(task.to_file_format())

    @classmethod
    def generate_reports(cls) -> None:
        """UC-11: Generate summary overview reports."""
        tasks = cls.load_tasks()
        users = cls.load_users()

        total = len(tasks)
        comp = sum(1 for t in tasks if t.completed)
        uncomp = total - comp
        overdue = sum(1 for t in tasks if t.is_overdue())

        p_inc = (uncomp / total * 100) if total > 0 else 0
        p_over = (overdue / total * 100) if total > 0 else 0

        with open(cls.TASK_OVERVIEW_FILE, "w") as f:
            f.write("======================================\n")
            f.write("         TASK OVERVIEW REPORT         \n")
            f.write("======================================\n")
            f.write(f"Total tasks generated:        {total}\n")
            f.write(f"Completed tasks:              {comp}\n")
            f.write(f"Uncompleted tasks:            {uncomp}\n")
            f.write(f"Overdue tasks:                {overdue}\n")
            f.write(f"Percentage incomplete:        {p_inc:.2f}%\n")
            f.write(f"Percentage overdue:           {p_over:.2f}%\n")

        with open(cls.USER_OVERVIEW_FILE, "w") as f:
            f.write("======================================\n")
            f.write("         USER OVERVIEW REPORT         \n")
            f.write("======================================\n")
            f.write(f"Total registered users:       {len(users)}\n")
            f.write(f"Total tasks generated:        {total}\n")
            f.write("--------------------------------------\n\n")

            for username in users:
                u_tasks = [t for t in tasks if t.username == username]
                u_tot = len(u_tasks)
                u_comp = sum(1 for t in u_tasks if t.completed)
                u_uncomp = u_tot - u_comp
                u_over = sum(1 for t in u_tasks if t.is_overdue())

                p_ass = (u_tot / total * 100) if total > 0 else 0
                p_c = (u_comp / u_tot * 100) if u_tot > 0 else 0
                p_i = (u_uncomp / u_tot * 100) if u_tot > 0 else 0
                p_o = (u_over / u_tot * 100) if u_tot > 0 else 0

                f.write(f"User: {username}\n")
                f.write(f"  - Total assigned:           {u_tot}\n")
                f.write(f"  - % of total tasks:         {p_ass:.2f}%\n")
                f.write(f"  - % completed:              {p_c:.2f}%\n")
                f.write(f"  - % to be completed:        {p_i:.2f}%\n")
                f.write(f"  - % overdue:                {p_o:.2f}%\n\n")

                