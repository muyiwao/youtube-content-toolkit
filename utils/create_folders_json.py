import os
import shutil
from pathlib import Path

def clean_directory(path: Path):
    """Deletes all files and subfolders inside the given directory."""
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def create_folders_with_json(base_directory: str, count: int = 10):
    base_path = Path(base_directory)

    # Normalize for logic checks
    base_name = base_directory.lower()

    # Create base directory if it doesn't exist
    base_path.mkdir(parents=True, exist_ok=True)

    # If directory is not empty → clean it
    if any(base_path.iterdir()):
        print(f"'{base_directory}' is not empty. Cleaning contents...")
        clean_directory(base_path)

    # Create subfolders & JSON files
    for i in range(1, count + 1):

        # Folder rules
        if base_name == "long":
            # Example: Long/1/1/1.json
            folder_path = base_path / str(i) / str(i)
        elif base_name == "shorts":
            # Example: Shorts/1/1.json
            folder_path = base_path / str(i)
        else:
            raise ValueError("Invalid base directory name.")

        json_file_path = folder_path / f"{i}.json"

        folder_path.mkdir(parents=True, exist_ok=True)
        json_file_path.touch()

    print(f"Successfully created {count} folders with empty JSON files in '{base_directory}'.")


# -------------------------
# User Input Section
# -------------------------

print("Choose folder path:")
print("1 = Long")
print("2 = Shorts")

choice = input("Enter 1 or 2: ").strip()

if choice == "1":
    folder = "Long"
elif choice == "2":
    folder = "Shorts"
else:
    print("Invalid selection! Please run again and choose 1 or 2.")
    exit()

# Ask for number of folders/json files
try:
    num = int(input("How many subfolders/json files to create? (Default = 10): ") or 10)
except ValueError:
    print("Invalid number! Using default value 10.")
    num = 10

# Execute
create_folders_with_json(folder, num)
