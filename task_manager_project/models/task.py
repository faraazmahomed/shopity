from datetime import datetime
from typing import Optional

DATE_FORMAT = "%d %b %Y"


class Task:
    """Represents a Task entity."""

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
        """Marks task completed."""
        self.completed = True

    def edit_details(
        self,
        new_username: Optional[str] = None,
        new_due_date: Optional[str] = None,
    ) -> None:
        """Edits task assignee and due date."""
        if self.completed:
            raise ValueError(
                "Completed tasks cannot be edited."
            )

        if new_username:
            self.username = new_username
        if new_due_date:
            self.due_date = new_due_date

    def is_overdue(self) -> bool:
        """Checks if task is overdue."""
        if self.completed:
            return False
        try:
            due = datetime.strptime(self.due_date, DATE_FORMAT)
            return due < datetime.now()
        except ValueError:
            return False

    def to_file_format(self) -> str:
        """Serializes task to text."""
        return (
            f"{self.username}, {self.title}, "
            f"{self.description}, {self.assigned_date}, "
            f"{self.due_date}, {self.completed_str}\n"
        )
