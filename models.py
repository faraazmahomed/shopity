from datetime import datetime
from typing import Optional


class User:
    """Represents a Standard User in the system."""

    def __init__(
        self, username: str, password: str, is_admin: bool = False
    ):
        self.username = username
        self.password = password
        self.is_admin = is_admin

    def to_file_format(self) -> str:
        """Serializes user object into comma-separated text."""
        return f"{self.username}, {self.password}\n"

    def __str__(self) -> str:
        role = "Admin" if self.is_admin else "Standard User"
        return f"User({self.username}, Role: {role})"


class AdminUser(User):
    """Represents an Admin User with extended privileges."""

    def __init__(self, username: str, password: str):
        super().__init__(username, password, is_admin=True)


class Task:
    """Represents a Task within the system."""

    def __init__(
        self,
        username: str,
        title: str,
        description: str,
        assigned_date: str,
        due_date: str,
        completed: bool = False,
        task_id: Optional[int] = None,
    ):
        self.task_id = task_id
        self.username = username
        self.title = title
        self.description = description
        self.assigned_date = assigned_date
        self.due_date = due_date
        self.completed = completed

    @property
    def completed_str(self) -> str:
        return "Yes" if self.completed else "No"

    def mark_complete(self) -> None:
        """UC-5: Mark Task Complete"""
        self.completed = True

    def edit_details(
        self,
        new_username: Optional[str] = None,
        new_due_date: Optional[str] = None,
    ) -> None:
        """UC-6: Edit Task Details (if task is incomplete)"""
        if self.completed:
            raise ValueError("Completed tasks cannot be edited.")

        if new_username:
            self.username = new_username
        if new_due_date:
            self.due_date = new_due_date

    def is_overdue(self) -> bool:
        """Checks if task is past due date and incomplete."""
        if self.completed:
            return False
        try:
            due = datetime.strptime(self.due_date, "%d %b %Y")
            return due < datetime.now()
        except ValueError:
            return False

    def to_file_format(self) -> str:
        """Serializes task into line-delimited format."""
        return (
            f"{self.username}, {self.title}, {self.description}, "
            f"{self.assigned_date}, {self.due_date}, "
            f"{self.completed_str}\n"
        )

    def __str__(self) -> str:
        status = "Yes" if self.completed else "No"
        return (
            f"Task ID: {self.task_id}\n"
            f"Task: {self.title}\n"
            f"Assigned to: {self.username}\n"
            f"Date assigned: {self.assigned_date}\n"
            f"Due date: {self.due_date}\n"
            f"Task complete? {status}\n"
            f"Task description: {self.description}\n"
        )