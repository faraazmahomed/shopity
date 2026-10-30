import os
from datetime import datetime, date

# Get user-agnostic base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILE_PATH = os.path.join(BASE_DIR, "user.txt")
TASKS_FILE_PATH = os.path.join(BASE_DIR, "tasks.txt")
TASK_OVERVIEW_PATH = os.path.join(BASE_DIR, "task_overview.txt")
USER_OVERVIEW_PATH = os.path.join(BASE_DIR, "user_overview.txt")

DATE_FORMAT = "%d %b %Y"


# ==========================================
# FILE HELPER FUNCTIONS
# ==========================================

def ensure_files_exist():
    """Ensures user.txt and tasks.txt exist prior to runtime."""
    if not os.path.exists(USER_FILE_PATH):
        with open(USER_FILE_PATH, "w") as file:
            file.write("admin, password\n")

    if not os.path.exists(TASKS_FILE_PATH):
        with open(TASKS_FILE_PATH, "w") as file:
            pass


def load_users():
    """Reads user.txt and returns dict of {username: password}."""
    users = {}
    if os.path.exists(USER_FILE_PATH):
        with open(USER_FILE_PATH, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(", ")
                    if len(parts) == 2:
                        users[parts[0]] = parts[1]
    return users


def load_tasks():
    """Reads tasks.txt and returns list of task dictionaries."""
    tasks = []
    if os.path.exists(TASKS_FILE_PATH):
        with open(TASKS_FILE_PATH, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(", ")
                if len(parts) == 6:
                    tasks.append({
                        "username": parts[0],
                        "title": parts[1],
                        "description": parts[2],
                        "assigned_date": parts[3],
                        "due_date": parts[4],
                        "completed": parts[5]
                    })
    return tasks


def save_tasks(tasks):
    """Overwrites tasks.txt with list of task dicts."""
    with open(TASKS_FILE_PATH, "w") as file:
        for t in tasks:
            entry = (
                f"{t['username']}, {t['title']}, "
                f"{t['description']}, {t['assigned_date']}, "
                f"{t['due_date']}, {t['completed']}\n"
            )
            file.write(entry)


def parse_date(date_str):
    """Parses date string into datetime object safely."""
    try:
        return datetime.strptime(date_str, DATE_FORMAT).date()
    except ValueError:
        return date.today()


# ==========================================
# CORE FEATURE FUNCTIONS
# ==========================================

def reg_user(users):
    """Registers new user, allowing cancellation by typing '-1'."""
    print("\n--- Register User ---")
    print("(Type '-1' at any prompt to cancel and return to main menu)\n")

    # Username validation loop
    while True:
        new_username = input("Enter new username: ").strip()

        if new_username == "-1":
            print("Registration cancelled.\n")
            return

        if new_username in users:
            print("Error: Username exists! Try another.\n")
        elif not new_username:
            print("Error: Username cannot be blank.\n")
        else:
            break

    # Password validation loop
    while True:
        new_password = input("Enter new password: ").strip()
        if new_password == "-1":
            print("Registration cancelled.\n")
            return
        if not new_password:
            print("Error: Password cannot be blank.\n")
            continue

        confirm_password = input("Confirm new password: ").strip()
        if confirm_password == "-1":
            print("Registration cancelled.\n")
            return

        if new_password == confirm_password:
            with open(USER_FILE_PATH, "a") as file:
                file.write(f"{new_username}, {new_password}\n")
            users[new_username] = new_password
            print(f"User '{new_username}' registered successfully!\n")
            break
        else:
            print("Error: Passwords do not match. Please try again.\n")


def add_task(users):
    """Adds a new task to tasks.txt, with cancellation support."""
    print("\n--- Add Task ---")
    print("(Type '-1' at any prompt to cancel and return to main menu)\n")

    while True:
        assigned_user = input("Person assigned to task: ").strip()
        if assigned_user == "-1":
            print("Task creation cancelled.\n")
            return
        if assigned_user in users:
            break
        print("Error: User does not exist. Enter a valid user.")

    title = input("Task title: ").strip()
    if title == "-1":
        print("Task creation cancelled.\n")
        return

    description = input("Task description: ").strip()
    if description == "-1":
        print("Task creation cancelled.\n")
        return

    while True:
        due_date_input = input(
            "Due date (e.g., 10 Oct 2026): "
        ).strip()
        if due_date_input == "-1":
            print("Task creation cancelled.\n")
            return
        try:
            datetime.strptime(due_date_input, DATE_FORMAT)
            break
        except ValueError:
            print("Invalid format! Use format like '10 Oct 2026'.")

    assigned_date = date.today().strftime(DATE_FORMAT)
    completed = "No"

    task_entry = (
        f"{assigned_user}, {title}, {description}, "
        f"{assigned_date}, {due_date_input}, {completed}\n"
    )
    with open(TASKS_FILE_PATH, "a") as file:
        file.write(task_entry)

    print("Task added successfully!\n")


def view_all():
    """Displays all tasks in tasks.txt."""
    print("\n=================== ALL TASKS ===================")
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.\n")
        return

    for t in tasks:
        print_task_formatted(t)
    print("=================================================\n")


def view_completed():
    """Displays all completed tasks."""
    print("\n================ COMPLETED TASKS ================")
    tasks = load_tasks()
    completed_tasks = [
        t for t in tasks if t['completed'].lower() == 'yes'
    ]

    if not completed_tasks:
        print("No completed tasks found.\n")
        return

    for t in completed_tasks:
        print_task_formatted(t)
    print("=================================================\n")


def delete_task():
    """Deletes a specific task selected by the admin user."""
    print("\n--- Delete a Task ---")
    tasks = load_tasks()
    if not tasks:
        print("No tasks available to delete.\n")
        return

    for idx, t in enumerate(tasks, 1):
        print(f"[{idx}] {t['title']} (Assigned to: {t['username']})")

    choice = input(
        "\nEnter task number to delete (or '-1' to cancel): "
    ).strip()

    if choice == '-1':
        print("Deletion cancelled.\n")
        return

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(tasks):
            removed = tasks.pop(index)
            save_tasks(tasks)
            print(
                f"Task '{removed['title']}' deleted successfully!\n"
            )
            return

    print("Invalid task number selected.\n")


def view_mine(logged_in_user, users):
    """Displays tasks for user and handles editing/completion."""
    print(
        f"\n================ MY TASKS ({logged_in_user}) ================"
    )
    tasks = load_tasks()

    my_tasks_map = {}
    display_counter = 1

    for orig_idx, t in enumerate(tasks):
        if t['username'] == logged_in_user:
            my_tasks_map[display_counter] = orig_idx
            print(f"Task Number: [{display_counter}]")
            print_task_formatted(t)
            display_counter += 1

    if not my_tasks_map:
        print("You currently have no tasks assigned to you.\n")
        return

    while True:
        user_input = input(
            "Enter task number to select, or '-1' for main menu: "
        ).strip()

        if user_input == "-1":
            return

        if user_input.isdigit() and int(user_input) in my_tasks_map:
            selected_num = int(user_input)
            break

        print("Invalid selection! Enter a valid task number.")

    target_idx = my_tasks_map[selected_num]
    selected_task = tasks[target_idx]

    print("\nOptions for selected task:")
    print("1 - Mark as complete")
    print("2 - Edit task")
    action = input("Select an option: ").strip()

    if action == "1":
        selected_task['completed'] = "Yes"
        save_tasks(tasks)
        print("Task marked as complete!\n")

    elif action == "2":
        if selected_task['completed'].lower() == "yes":
            print("Completed tasks cannot be edited.\n")
            return

        print("\nEdit Options:")
        print("1 - Edit assigned user")
        print("2 - Edit due date")
        print("3 - Edit both")
        edit_choice = input("Select an option: ").strip()

        if edit_choice in ["1", "3"]:
            new_assignee = input(
                "Enter new assigned username: "
            ).strip()
            if new_assignee in users:
                selected_task['username'] = new_assignee
            else:
                print("User does not exist. Assignee not changed.")

        if edit_choice in ["2", "3"]:
            new_due = input(
                "Enter new due date (e.g., 10 Oct 2026): "
            ).strip()
            try:
                datetime.strptime(new_due, DATE_FORMAT)
                selected_task['due_date'] = new_due
            except ValueError:
                print("Invalid format. Due date not changed.")

        save_tasks(tasks)
        print("Task updated successfully!\n")


def generate_reports():
    """Generates task_overview.txt and user_overview.txt."""
    tasks = load_tasks()
    users = load_users()
    today = date.today()

    total_tasks = len(tasks)
    completed_tasks = sum(
        1 for t in tasks if t['completed'].lower() == 'yes'
    )
    uncompleted_tasks = total_tasks - completed_tasks

    overdue_tasks = sum(
        1 for t in tasks
        if t['completed'].lower() == 'no'
        and parse_date(t['due_date']) < today
    )

    pct_inc = (
        (uncompleted_tasks / total_tasks * 100)
        if total_tasks > 0 else 0
    )
    pct_over = (
        (overdue_tasks / total_tasks * 100)
        if total_tasks > 0 else 0
    )

    # Write task_overview.txt
    with open(TASK_OVERVIEW_PATH, "w") as file:
        file.write("==================================================\n")
        file.write("                  TASK OVERVIEW                   \n")
        file.write("==================================================\n")
        file.write(f"Total tasks:                         {total_tasks}\n")
        file.write(f"Completed tasks:                     {completed_tasks}\n")
        file.write(f"Uncompleted tasks:                 {uncompleted_tasks}\n")
        file.write(f"Overdue & uncompleted tasks:         {overdue_tasks}\n")
        file.write(f"Percentage of tasks incomplete:      {pct_inc:.2f}%\n")
        file.write(f"Percentage of tasks overdue:         {pct_over:.2f}%\n")
        file.write("==================================================\n")

    # Write user_overview.txt
    total_users = len(users)
    with open(USER_OVERVIEW_PATH, "w") as file:
        file.write("==================================================\n")
        file.write("                  USER OVERVIEW                   \n")
        file.write("==================================================\n")
        file.write(f"Total users registered:              {total_users}\n")
        file.write(f"Total tasks generated:               {total_tasks}\n")
        file.write("--------------------------------------------------\n")

        for u in users:
            u_tasks = [t for t in tasks if t['username'] == u]
            u_total = len(u_tasks)
            u_comp = sum(
                1 for t in u_tasks if t['completed'].lower() == 'yes'
            )
            u_uncomp = u_total - u_comp
            u_over = sum(
                1 for t in u_tasks
                if t['completed'].lower() == 'no'
                and parse_date(t['due_date']) < today
            )

            u_pct_assigned = (
                (u_total / total_tasks * 100)
                if total_tasks > 0 else 0
            )
            u_pct_comp = (
                (u_comp / u_total * 100) if u_total > 0 else 0
            )
            u_pct_uncomp = (
                (u_uncomp / u_total * 100) if u_total > 0 else 0
            )
            u_pct_over = (
                (u_over / u_total * 100) if u_total > 0 else 0
            )

            file.write(f"USER: {u}\n")
            file.write(
                f"  - Tasks assigned:                  {u_total}\n"
            )
            file.write(
                f"  - % of total system tasks:         {u_pct_assigned:.2f}%\n"
            )
            file.write(
                f"  - % assigned tasks completed:      {u_pct_comp:.2f}%\n"
            )
            file.write(
                f"  - % assigned tasks to complete:    {u_pct_uncomp:.2f}%\n"
            )
            file.write(
                f"  - % assigned tasks overdue:        {u_pct_over:.2f}%\n"
            )
            file.write("--------------------------------------------------\n")

    print(
        "Reports generated: 'task_overview.txt' & "
        "'user_overview.txt'\n"
    )


def display_statistics():
    """Reads and displays task_overview.txt and user_overview.txt."""
    if (
        not os.path.exists(TASK_OVERVIEW_PATH)
        or not os.path.exists(USER_OVERVIEW_PATH)
    ):
        print("Overview files not found. Generating reports first...\n")
        generate_reports()

    print("\n--- DISPLAY STATISTICS ---")
    with open(TASK_OVERVIEW_PATH, "r") as file:
        print(file.read())

    with open(USER_OVERVIEW_PATH, "r") as file:
        print(file.read())


def print_task_formatted(task):
    """Helper formatting function for displaying tasks cleanly."""
    print("-" * 50)
    print(f"Task:             {task['title']}")
    print(f"Assigned to:      {task['username']}")
    print(f"Date assigned:    {task['assigned_date']}")
    print(f"Due date:         {task['due_date']}")
    print(f"Task Completed?   {task['completed']}")
    print(f"Task Description:\n {task['description']}")
    print("-" * 50)


# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    ensure_files_exist()
    users = load_users()

    # Login sequence
    logged_in_user = ""
    while True:
        username_input = input("Enter username: ").strip()
        password_input = input("Enter password: ").strip()

        if username_input not in users:
            print("Username not recognized. Please try again.\n")
        elif users[username_input] != password_input:
            print("Incorrect password. Please try again.\n")
        else:
            print(f"\nLogin successful! Welcome, {username_input}.\n")
            logged_in_user = username_input
            break

    # Menus
    admin_menu = (
        "Please select one of the following options:\n"
        "r   - register user\n"
        "a   - add task\n"
        "va  - view all tasks\n"
        "vm  - view my tasks\n"
        "vc  - view completed tasks\n"
        "del - delete a task\n"
        "ds  - display statistics\n"
        "gr  - generate reports\n"
        "e   - exit\n"
        ": "
    )

    user_menu = (
        "Please select one of the following options:\n"
        "a   - add task\n"
        "va  - view all tasks\n"
        "vm  - view my tasks\n"
        "e   - exit\n"
        ": "
    )

    while True:
        if logged_in_user == "admin":
            menu = input(admin_menu).lower().strip()
        else:
            menu = input(user_menu).lower().strip()

        if menu == 'r':
            if logged_in_user == "admin":
                reg_user(users)
            else:
                print("Access denied. Only 'admin' can register.\n")

        elif menu == 'a':
            add_task(users)

        elif menu == 'va':
            view_all()

        elif menu == 'vm':
            view_mine(logged_in_user, users)

        elif menu == 'vc':
            if logged_in_user == "admin":
                view_completed()
            else:
                print("Invalid option. Please try again.\n")

        elif menu == 'del':
            if logged_in_user == "admin":
                delete_task()
            else:
                print("Invalid option. Please try again.\n")

        elif menu == 'gr':
            if logged_in_user == "admin":
                generate_reports()
            else:
                print("Invalid option. Please try again.\n")

        elif menu == 'ds':
            if logged_in_user == "admin":
                display_statistics()
            else:
                print("Invalid option. Please try again.\n")

        elif menu == 'e':
            print("Goodbye!!!")
            break

        else:
            print("Invalid input. Please try again.\n")


if __name__ == "__main__":
    main()
