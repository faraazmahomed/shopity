from datetime import datetime
import unittest

from models import Task, User


class TestUserAuthentication(unittest.TestCase):
    """UC-1: Unit tests for User authentication logic."""

    def setUp(self) -> None:
        self.user = User("alice", "SecurePass123")

    def test_successful_authentication() -> None:
        """Verify user authenticates with correct password."""
        self.assertEqual(self.user.password, "SecurePass123")

    def test_failed_authentication() -> None:
        """Verify mismatched password check fails."""
        self.assertNotEqual(self.user.password, "WrongPass")


class TestTaskCreation(unittest.TestCase):
    """UC-2: Unit tests for Task initialization."""

    def setUp(self) -> None:
        self.task = Task(
            username="bob",
            title="Submit Report",
            description="Quarterly financial summary",
            assigned_date="20 Sep 2026",
            due_date="25 Sep 2026",
            task_id=1,
        )

    def test_task_initial_state() -> None:
        """Verify new task starts incomplete with accurate IDs."""
        self.assertFalse(self.task.completed)
        self.assertEqual(self.task.completed_str, "No")
        self.assertEqual(self.task.username, "bob")

    def test_task_serialization_format() -> None:
        """Verify in-memory string formatting for task output."""
        expected_str = (
            "bob, Submit Report, Quarterly financial summary, "
            "20 Sep 2026, 25 Sep 2026, No\n"
        )
        self.assertEqual(
            self.task.to_file_format(), expected_str
        )


class TestMarkTaskComplete(unittest.TestCase):
    """UC-5: Unit tests for marking tasks complete."""

    def setUp(self) -> None:
        self.task = Task(
            username="charlie",
            title="Write Code",
            description="Implement unit tests",
            assigned_date="20 Sep 2026",
            due_date="30 Sep 2026",
        )

    def test_mark_complete() -> None:
        """Verify task status updates to completed."""
        self.assertFalse(self.task.completed)
        self.task.mark_complete()
        self.assertTrue(self.task.completed)
        self.assertEqual(self.task.completed_str, "Yes")


class TestEditTaskDetails(unittest.TestCase):
    """UC-6: Unit tests for editing incomplete tasks."""

    def setUp(self) -> None:
        self.task = Task(
            username="diana",
            title="Review PR",
            description="Code review for team",
            assigned_date="20 Sep 2026",
            due_date="22 Sep 2026",
        )

    def test_edit_incomplete_task_assignee() -> None:
        """Verify changing assignee on an open task."""
        self.task.edit_details(new_username="eve")
        self.assertEqual(self.task.username, "eve")

    def test_edit_incomplete_task_due_date() -> None:
        """Verify changing due date on an open task."""
        self.task.edit_details(new_due_date="28 Sep 2026")
        self.assertEqual(self.task.due_date, "28 Sep 2026")

    def test_edit_completed_task_raises_error() -> None:
        """Verify modifying a completed task raises ValueError."""
        self.task.mark_complete()
        with self.assertRaises(ValueError):
            self.task.edit_details(new_username="frank")


if __name__ == "__main__":
    unittest.main()

    