"""
E-Bookstore Database Management System.

Provides CLI functionality to manage books and authors stored in an
SQLite database with robust error handling and modular design.
"""

import sqlite3
from typing import Optional


# ==========================================
# DATABASE CONNECTION AND SETUP
# ==========================================

DB_NAME = "ebookstore.db"


def get_connection():
    """Returns a database connection with foreign key support."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database() -> None:
    """Creates tables and populates default data if empty."""
    create_author_table = """
    CREATE TABLE IF NOT EXISTS author (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        country TEXT NOT NULL
    );
    """
    create_book_table = """
    CREATE TABLE IF NOT EXISTS book (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author INTEGER NOT NULL,
        qty INTEGER NOT NULL,
        FOREIGN KEY (author) REFERENCES author(id)
            ON DELETE CASCADE
    );
    """
    initial_authors = [
        (1290, "Charles Dickens", "United Kingdom"),
        (8937, "J.K. Rowling", "United Kingdom"),
        (2356, "C.S. Lewis", "United Kingdom"),
        (6380, "J.R.R. Tolkien", "United Kingdom"),
        (5620, "Lewis Carroll", "United Kingdom"),
    ]
    initial_books = [
        (3001, "A Tale of Two Cities", 1290, 30),
        (3002, "Harry Potter", 8937, 40),
        (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
        (3004, "The Lord of the Rings", 6380, 37),
        (3005, "Alices Adventures in Wonderland", 5620, 12),
    ]

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_author_table)
            cursor.execute(create_book_table)

            # Populate initial data if author table is empty
            cursor.execute("SELECT COUNT(*) FROM author;")
            if cursor.fetchone()[0] == 0:
                cursor.executemany(
                    "INSERT INTO author VALUES (?, ?, ?);",
                    initial_authors,
                )
                cursor.executemany(
                    "INSERT INTO book VALUES (?, ?, ?, ?);",
                    initial_books,
                )
    except sqlite3.Error as err:
        print(f"\n[Database Initialization Error]: {err}")


# ==========================================
# INPUT VALIDATION HELPERS
# ==========================================


def prompt_four_digit_id(prompt_msg: str) -> Optional[int]:
    """Prompts for and validates a 4-digit positive integer ID."""
    user_input = input(prompt_msg).strip()
    if not (user_input.isdigit() and len(user_input) == 4):
        print("\n[Error]: ID must be exactly a 4-digit integer.")
        return None
    return int(user_input)


def prompt_non_empty_string(prompt_msg: str) -> Optional[str]:
    """Prompts for and validates non-empty string input."""
    user_input = input(prompt_msg).strip()
    if not user_input:
        print("\n[Error]: Input cannot be empty.")
        return None
    return user_input


def prompt_positive_int(prompt_msg: str) -> Optional[int]:
    """Prompts for and validates a positive integer quantity."""
    user_input = input(prompt_msg).strip()
    if not user_input.isdigit():
        print(
            "\n[Error]: Quantity must be a valid positive integer."
        )
        return None
    return int(user_input)


# ==========================================
# CRUD OPERATIONS
# ==========================================


def add_new_book() -> None:
    """Adds a new book and author record into the database."""
    print("\n--- ADD NEW BOOK ---")
    book_id = prompt_four_digit_id("Enter 4-digit Book ID: ")
    if book_id is None:
        return

    title = prompt_non_empty_string("Enter Book Title: ")
    if title is None:
        return

    author_id = prompt_four_digit_id("Enter 4-digit Author ID: ")
    if author_id is None:
        return

    author_name = prompt_non_empty_string("Enter Author Name: ")
    if author_name is None:
        return

    country = prompt_non_empty_string("Enter Author Country: ")
    if country is None:
        return

    qty = prompt_positive_int("Enter Quantity: ")
    if qty is None:
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Insert author if it doesn't already exist
            cursor.execute(
                """
                INSERT OR IGNORE INTO author (id, name, country)
                VALUES (?, ?, ?);
                """,
                (author_id, author_name, country),
            )
            # Insert book record
            cursor.execute(
                """
                INSERT INTO book (id, title, author, qty)
                VALUES (?, ?, ?, ?);
                """,
                (book_id, title, author_id, qty),
            )
            print(
                f"\n[Success]: Book '{title}' added successfully!"
            )
    except sqlite3.IntegrityError:
        print(f"\n[Error]: Book ID {book_id} already exists.")
    except sqlite3.Error as err:
        print(f"\n[Database Error]: {err}")


def update_book_details() -> None:
    """Allows updating book quantity, title, or author details."""
    print("\n--- UPDATE BOOK DETAILS ---")
    book_id = prompt_four_digit_id("Enter 4-digit Book ID: ")
    if book_id is None:
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            fetch_query = """
                SELECT b.id, b.title, b.qty, a.id, a.name, a.country
                FROM book b
                INNER JOIN author a ON b.author = a.id
                WHERE b.id = ?;
            """
            cursor.execute(fetch_query, (book_id,))
            record = cursor.fetchone()

            if not record:
                print(f"\n[Error]: No book found with ID {book_id}.")
                return

            b_id, title, qty, author_id, author_name, country = (
                record
            )

            print("\n" + "=" * 50)
            print(f"Book Found: '{title}' (ID: {b_id})")
            print(f"Current Quantity : {qty}")
            print(f"Current Author   : {author_name} ({country})")
            print("=" * 50)

            print("\nWhat would you like to update?")
            print("1. Update Quantity")
            print("2. Update Book Title")
            print("3. Update Author Details (Name / Country)")
            print("0. Cancel")

            choice = input("Enter choice (0-3): ").strip()

            if choice == "1":
                new_qty = prompt_positive_int("Enter new quantity: ")
                if new_qty is None:
                    return
                cursor.execute(
                    "UPDATE book SET qty = ? WHERE id = ?;",
                    (new_qty, book_id),
                )
                print(f"\n[Success]: Quantity updated to {new_qty}.")

            elif choice == "2":
                new_title = prompt_non_empty_string("Enter title: ")
                if new_title is None:
                    return
                cursor.execute(
                    "UPDATE book SET title = ? WHERE id = ?;",
                    (new_title, book_id),
                )
                print(
                    f"\n[Success]: Title updated to '{new_title}'."
                )

            elif choice == "3":
                print(
                    "\nEnter details (or press Enter to keep current):"
                )
                p_name = f"New Author Name [{author_name}]: "
                new_name = input(p_name).strip()
                p_country = f"New Country [{country}]: "
                new_country = input(p_country).strip()

                u_name = new_name if new_name else author_name
                u_country = new_country if new_country else country

                if u_name == author_name and u_country == country:
                    print("\nNo changes made.")
                    return

                cursor.execute(
                    """
                    UPDATE author
                    SET name = ?, country = ?
                    WHERE id = ?;
                    """,
                    (u_name, u_country, author_id),
                )
                print(
                    "\n[Success]: Author details updated!"
                )

            elif choice == "0":
                print("\nUpdate cancelled.")
                return

            else:
                print(
                    "\n[Error]: Invalid option. Returning to menu."
                )

    except sqlite3.Error as err:
        print(f"\n[Database Error]: {err}")


def delete_book() -> None:
    """Deletes a book from the database by its ID."""
    print("\n--- DELETE BOOK ---")
    book_id = prompt_four_digit_id(
        "Enter 4-digit Book ID to delete: "
    )
    if book_id is None:
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM book WHERE id = ?;", (book_id,)
            )
            if cursor.rowcount == 0:
                print(f"\n[Error]: No book found with ID {book_id}.")
            else:
                print(f"\n[Success]: Book ID {book_id} deleted.")
    except sqlite3.Error as err:
        print(f"\n[Database Error]: {err}")


def search_book() -> None:
    """Searches for a book by its 4-digit ID and displays details."""
    print("\n--- SEARCH BOOK ---")
    book_id = prompt_four_digit_id("Enter 4-digit Book ID: ")
    if book_id is None:
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT b.id, b.title, a.name, a.country, b.qty
                FROM book b
                INNER JOIN author a ON b.author = a.id
                WHERE b.id = ?;
            """
            cursor.execute(query, (book_id,))
            result = cursor.fetchone()

            if not result:
                print(f"\n[Error]: No book found with ID {book_id}.")
                return

            b_id, title, author, country, qty = result
            print("\n" + "=" * 65)
            print(f"ID      : {b_id}")
            print(f"Title   : {title}")
            print(f"Author  : {author}")
            print(f"Country : {country}")
            print(f"Stock   : {qty}")
            print("=" * 65)

    except sqlite3.Error as err:
        print(f"\n[Database Error]: {err}")


def view_all_books() -> None:
    """
    Fetches all books and uses zip() to combine and present title,
    author, and country in a formatted table.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT b.title, a.name, a.country
                FROM book b
                INNER JOIN author a ON b.author = a.id;
            """
            cursor.execute(query)
            records = cursor.fetchall()

            if not records:
                print("\nNo books found in the database.")
                return

            titles = [r[0] for r in records]
            authors = [r[1] for r in records]
            countries = [r[2] for r in records]

            print("\n" + "=" * 67)
            print(
                f"{'TITLE':<32} | {'AUTHOR':<18} | {'COUNTRY':<12}"
            )
            print("=" * 67)

            for title, author, country in zip(
                titles, authors, countries
            ):
                t_fmt = (
                    title[:30] + ".." if len(title) > 32 else title
                )
                a_fmt = (
                    author[:16] + ".." if len(author) > 18 else author
                )
                print(
                    f"{t_fmt:<32} | {a_fmt:<18} | {country:<12}"
                )

            print("=" * 67)

    except sqlite3.Error as err:
        print(f"\n[Database Error]: {err}")


# ==========================================
# MAIN APPLICATION LOOP
# ==========================================


def display_menu() -> None:
    """Prints the main interactive CLI menu."""
    print("\n" + "=" * 35)
    print("      E-BOOKSTORE MENU")
    print("=" * 35)
    print("1. Enter book")
    print("2. Update book")
    print("3. Delete book")
    print("4. Search book")
    print("5. View details of all books")
    print("0. Exit")
    print("=" * 35)


def main() -> None:
    """Program entry point."""
    initialize_database()

    actions = {
        "1": add_new_book,
        "2": update_book_details,
        "3": delete_book,
        "4": search_book,
        "5": view_all_books,
    }

    while True:
        display_menu()
        choice = input("Enter your selection (0-5): ").strip()

        if choice == "0":
            print("\nGoodbye! Thank you for using E-Bookstore.")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print(
                "\n[Error]: Invalid selection. Please choose 0 to 5."
            )


if __name__ == "__main__":
    main()
