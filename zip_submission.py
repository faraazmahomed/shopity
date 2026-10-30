import os
import zipfile

# Directory to compress and output zip name
PROJECT_DIR = "."
OUTPUT_ZIP = "task_manager_submission.zip"

# Directories and extensions/files to exclude
EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    ".pytest_cache",
    ".idea",
    ".vscode",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".DS_Store",
}

EXCLUDE_FILES = {
    OUTPUT_ZIP,
    "task_overview.txt",
    "user_overview.txt",
}


def create_submission_zip():
    print(f"Creating submission zip: {OUTPUT_ZIP}...\n")
    zipped_count = 0

    with zipfile.ZipFile(
        OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED
    ) as zipf:
        for root, dirs, files in os.walk(PROJECT_DIR):
            # Prune excluded directories in-place
            dirs[:] = [
                d for d in dirs if d not in EXCLUDE_DIRS
            ]

            for file in files:
                if file in EXCLUDE_FILES:
                    continue

                _, ext = os.path.splitext(file)
                if ext in EXCLUDE_EXTENSIONS:
                    continue

                file_path = os.path.join(root, file)
                # Maintain relative path inside the zip archive
                arcname = os.path.relpath(
                    file_path, start=PROJECT_DIR
                )

                zipf.write(file_path, arcname)
                print(f"  [+] Added: {arcname}")
                zipped_count += 1

    print(
        f"\nDone! Successfully packaged {zipped_count} "
        f"files into '{OUTPUT_ZIP}'."
    )


if __name__ == "__main__":
    create_submission_zip()

    