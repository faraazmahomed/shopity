import sys
from pathlib import Path
import unittest
from models.user import User
from models.task import Task


# Add the project root directory to sys.path so 'models' can be imported 
# regardless of how or from where the script is executed.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestUserAuthentication(unittest.TestCase):
    """Tests user authentication functionality."""

    def setUp(self) -> None:
        self.user = User("alice", "SecurePass123")

    def test_successful_authentication(self) -> None:
        self.assertTrue(self.user.authenticate("SecurePass123"))

    def test_failed_authentication(self) -> None:
        self.assertFalse(self.user.authenticate("WrongPass"))


class TestTaskCreation(unittest.TestCase):
    """Tests task creation and serialization."""

    def setUp(self) -> None:
        self.task = Task(
            task_id=1,
            username="bob",
            title="Submit Report",
            description="Quarterly summary",
            assigned_date="20 Sep 2026",
            due_date="25 Sep 2026",
        )

    def test_task_initial_state(self) -> None:
        self.assertFalse(self.task.completed)
        self.assertEqual(self.task.completed_str, "No")
        self.assertEqual(self.task.username, "bob")

    def test_task_serialization_format(self) -> None:
        expected_str = (
            "bob, Submit Report, Quarterly summary, "
            "20 Sep 2026, 25 Sep 2026, No\n"
        )
        self.assertEqual(self.task.to_file_format(), expected_str)


class TestMarkTaskComplete(unittest.TestCase):
    """Tests marking a task as complete."""

    def setUp(self) -> None:
        self.task = Task(
            task_id=2,
            username="charlie",
            title="Write Code",
            description="Implement tests",
            assigned_date="20 Sep 2026",
            due_date="30 Sep 2026",
        )

    def test_mark_complete(self) -> None:
        self.assertFalse(self.task.completed)
        self.task.mark_complete()
        self.assertTrue(self.task.completed)


if __name__ == "__main__":
    unittest.main()
