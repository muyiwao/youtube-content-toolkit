#!/usr/bin/env python3
"""
cleanup_muyverse_downloads.py

Deletes all files and folders inside the specified subfolders
(Long, Reels, Shorts) while keeping the parent folders intact.

Usage examples:
# run in current folder (recommended if you cd into Muyverse Downloads)
python cleanup_muyverse_downloads.py

# specify a path explicitly
python cleanup_muyverse_downloads.py --path "C:/Users/Muy/Muyverse Downloads"

# show what would be deleted but do not delete
python cleanup_muyverse_downloads.py --dry-run

# skip confirmation and delete immediately
python cleanup_muyverse_downloads.py --yes
"""

from pathlib import Path
import shutil
import argparse
import sys

SUBFOLDERS = ["Long", "Reels", "Shorts"]

def gather_items(folder: Path):
    """Return list of items (Path) that would be deleted inside folder."""
    if not folder.exists():
        return None
    return [p for p in folder.iterdir()]

def human_size(nbytes: int) -> str:
    """Return a human readable size string."""
    for unit in ("B","KB","MB","GB","TB"):
        if nbytes < 1024.0:
            return f"{nbytes:3.1f}{unit}"
        nbytes /= 1024.0
    return f"{nbytes:.1f}PB"

def preview_and_confirm(base_dir: Path, dry_run: bool, auto_yes: bool):
    """Show preview of deletions and ask the user to confirm."""
    print(f"\nTarget base directory: {base_dir}")
    total_items = 0
    total_bytes = 0
    previews = {}

    for sub in SUBFOLDERS:
        folder = base_dir / sub
        items = gather_items(folder)
        if items is None:
            print(f"  ❌ Not found: {folder}")
            previews[sub] = None
            continue

        count = len(items)
        size = 0
        for p in items:
            try:
                if p.is_file():
                    size += p.stat().st_size
                elif p.is_dir():
                    for subp in p.rglob('*'):
                        if subp.is_file():
                            size += subp.stat().st_size
            except Exception:
                pass
        previews[sub] = (count, size)
        total_items += count
        total_bytes += size

    print("\nPreview of contents to be removed:")
    for sub, info in previews.items():
        if info is None:
            print(f"  {sub}: folder not found")
        else:
            count, size = info
            print(f"  {sub}: {count} items, approx {human_size(size)}")

    print(f"\nTotal approx size: {human_size(total_bytes)} across {total_items} items.\n")

    if dry_run:
        print("Dry run enabled. No files will be deleted.")
        return False

    if auto_yes:
        return True

    reply = input("Proceed to delete all contents of the above folders? Type 'yes' to confirm: ").strip().lower()
    return reply == "yes"

def clear_folder_contents(folder: Path):
    """Delete all files and subfolders inside folder but keep the folder itself."""
    if not folder.exists():
        print(f"  ❌ Folder not found: {folder}")
        return
    for item in folder.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                print(f"  🗑 Deleted file: {item}")
            elif item.is_dir():
                shutil.rmtree(item)
                print(f"  🧹 Deleted folder: {item}")
        except Exception as e:
            print(f"  ⚠ Failed to delete {item}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Clean contents of Long, Reels, Shorts in Muyverse Downloads")
    parser.add_argument("--path", "-p", type=str, default=None,
                        help="Path to MUYVERSE DOWNLOADS directory. If omitted, uses current working directory.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt and proceed")

    args = parser.parse_args()

    if args.path:
        base_dir = Path(args.path).expanduser().resolve()
    else:
        base_dir = Path.cwd()

    found_any = any((base_dir / s).exists() for s in SUBFOLDERS)
    if not found_any:
        print(f"\nError: None of the expected subfolders {SUBFOLDERS} were found in {base_dir}")
        print("If you intended to target a different folder, re-run with --path \"C:/path/to/Muyverse Downloads\"")
        sys.exit(1)

    proceed = preview_and_confirm(base_dir, dry_run=args.dry_run, auto_yes=args.yes)
    if not proceed:
        print("Aborted. No files were deleted.")
        return

    print("\n🧽 Starting deletion...")
    for sub in SUBFOLDERS:
        folder = base_dir / sub
        if folder.exists():
            clear_folder_contents(folder)
        else:
            print(f"  ❌ Folder not found: {folder}")
    print("\n✅ Cleanup complete.")

if __name__ == "__main__":
    main()
