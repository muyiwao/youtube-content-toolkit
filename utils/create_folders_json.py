import os
import shutil
from pathlib import Path

# ---------------------------------------------------------
# Utility: Remove everything inside a directory
# ---------------------------------------------------------
def clean_directory(path: Path):
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


# ---------------------------------------------------------
# Utility: Parse ranges such as "1-10", "3", "1-5,7,10-12"
# ---------------------------------------------------------
def parse_range_input(range_text: str):
    """
    Converts string like "1-5,8,10-12" into a sorted list of ints.
    """
    selected = set()

    parts = range_text.replace(" ", "").split(",")
    for part in parts:
        if "-" in part:
            start, end = part.split("-")
            if start.isdigit() and end.isdigit():
                selected.update(range(int(start), int(end) + 1))
        elif part.isdigit():
            selected.add(int(part))
        else:
            raise ValueError(f"Invalid range format: {part}")

    return sorted(selected)


# ---------------------------------------------------------
# Main function: create folders & JSON based on parsed range
# ---------------------------------------------------------
def create_folders_with_json(base_directory: str, folder_numbers: list):
    base_path = Path(base_directory)
    base_name = base_directory.lower()

    # Create base directory if missing
    base_path.mkdir(parents=True, exist_ok=True)

    # Clean directory before creating new structure
    if any(base_path.iterdir()):
        print(f"'{base_directory}' is not empty. Cleaning contents...")
        clean_directory(base_path)

    # Build folder structures
    for num in folder_numbers:
        if base_name == "long":
            folder_path = base_path / str(num) / str(num)
        elif base_name == "shorts":
            folder_path = base_path / str(num)
        else:
            raise ValueError("Invalid base directory. Must be 'Long' or 'Shorts'.")

        json_file = folder_path / f"{num}.json"

        folder_path.mkdir(parents=True, exist_ok=True)
        json_file.touch()

    print(f"Successfully created {len(folder_numbers)} folders in '{base_directory}'.")
    print(f"Folders created: {folder_numbers}")


# ---------------------------------------------------------
# USER INPUT SECTION
# ---------------------------------------------------------

print("Choose folder group:")
print("1 = Long")
print("2 = Shorts")

choice = input("Enter 1 or 2: ").strip()

if choice == "1":
    folder = "Long"
elif choice == "2":
    folder = "Shorts"
else:
    print("Invalid selection. Exiting.")
    exit()

# Ask for range input
print("\nEnter folder numbers or ranges (examples: 5, 1-10, 3-7, 1-3,7,10-12)")
range_text = input("Folder range: ").strip()

try:
    folder_numbers = parse_range_input(range_text)
except Exception as e:
    print(f"Error: {e}")
    exit()

# Execute creation
create_folders_with_json(folder, folder_numbers)
