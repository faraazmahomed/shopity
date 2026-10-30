class Email:
    """Class for representing an email object."""

    def __init__(self, email_address, subject_line, email_content):
        

        self.email_address = email_address
        self.subject_line = subject_line
        self.email_content = email_content
        self.has_been_read = False

    def mark_as_read(self):
        
        self.has_been_read = True


def populate_inbox():
    

    emails = [
        Email(
            "person1@hyperiondev.com",
            "Welcome to HyperionDev!",
            "This is your welcome email.",
        ),
        Email(
            "person2@hyperiondev.com",
            "Great work on the bootcamp!",
            "You're making great progress!",
        ),
        Email(
            "person3@hyperiondev.com",
            "Your excellent marks!",
            "You're doing amazing, keep it up!",
        ),
    ]
    inbox.extend(emails)


def list_emails():
   
    print("\nInbox:")
    for index, email in enumerate(inbox):
        print(f"{index}. {email.subject_line}")


def read_email(index):
    """
    Displays details of the selected email based on its index.

    Args:
        index (int): The index of the selected email in the inbox list.
    """

    # Checks if the selected email number corresponds to an email in the inbox
    if index >= 0 and index < len(inbox):
        email = inbox[index]
        print("\nSelected email details:")
        print(f"\nFrom: {email.email_address}")
        print(f"Subject: {email.subject_line}")
        print(f"Content: {email.email_content}")

        # Mark the email as read if it hasn't already been read
        if not email.has_been_read:
            email.mark_as_read()
            print(f"\nEmail from {email.email_address} marked as read.\n")

    else:
        print("Invalid email number.")


def view_unread_emails():
    """
    Displays all the unread email subject lines with their corresponding
    index number with the inbox.
    """

    print("\nUnread Emails:")
    for index, email in enumerate(inbox):
        if not email.has_been_read:
            print(f"{index}. {email.subject_line}")

inbox = []

# Populating 'inbox' with initial Email objects.
populate_inbox()

# Main Program
while True:
    menu = """
Would you like to:
    1. Read an email
    2. View unread emails
    3. Quit application

Enter selection:
"""

    user_choice = input(menu)

    if user_choice == "1":
        list_emails()
        index = int(input("Enter the number of the email you want to read: "))
        read_email(index)
    elif user_choice == "2":
        view_unread_emails()
    elif user_choice == "3":
        print("Quitting application.")
        break
    else:
        print("Invalid choice. Please select again.")