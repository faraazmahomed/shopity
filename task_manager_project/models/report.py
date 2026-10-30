from typing import Dict, List
from models.task import Task
from models.user import User


class ReportGenerator:
    """Calculates report metrics."""

    @staticmethod
    def generate_task_report(tasks: List[Task]) -> str:
        """Generates task overview string."""
        total = len(tasks)
        comp = sum(1 for t in tasks if t.completed)
        uncomp = total - comp
        overdue = sum(1 for t in tasks if t.is_overdue())

        p_inc = (uncomp / total * 100) if total > 0 else 0
        p_over = (overdue / total * 100) if total > 0 else 0

        return (
            "======================================\n"
            "         TASK OVERVIEW REPORT         \n"
            "======================================\n"
            f"Total tasks generated:        {total}\n"
            f"Completed tasks:              {comp}\n"
            f"Uncompleted tasks:            {uncomp}\n"
            f"Overdue tasks:                {overdue}\n"
            f"Percentage incomplete:        {p_inc:.2f}%\n"
            f"Percentage overdue:           {p_over:.2f}%\n"
        )

    @staticmethod
    def generate_user_report(
        users: Dict[str, User], tasks: List[Task]
    ) -> str:
        """Generates user overview string."""
        total = len(tasks)
        lines = [
            "======================================\n",
            "         USER OVERVIEW REPORT         \n",
            "======================================\n",
            f"Total registered users:       {len(users)}\n",
            f"Total tasks generated:        {total}\n",
            "--------------------------------------\n\n",
        ]

        for username in users:
            u_tasks = [
                t for t in tasks if t.username == username
            ]
            u_tot = len(u_tasks)
            u_comp = sum(1 for t in u_tasks if t.completed)
            u_uncomp = u_tot - u_comp
            u_over = sum(1 for t in u_tasks if t.is_overdue())

            p_ass = (u_tot / total * 100) if total > 0 else 0
            p_c = (u_comp / u_tot * 100) if u_tot > 0 else 0
            p_i = (u_uncomp / u_tot * 100) if u_tot > 0 else 0
            p_o = (u_over / u_tot * 100) if u_tot > 0 else 0

            lines.append(f"User: {username}\n")
            lines.append(
                f"  - Total assigned:           {u_tot}\n"
            )
            lines.append(
                f"  - % of total tasks:         {p_ass:.2f}%\n"
            )
            lines.append(
                f"  - % completed:              {p_c:.2f}%\n"
            )
            lines.append(
                f"  - % to be completed:        {p_i:.2f}%\n"
            )
            lines.append(
                f"  - % overdue:                {p_o:.2f}%\n\n"
            )

        return "".join(lines)
