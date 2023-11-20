# %%
# Standard Library
import os


def print_folder_structure(
    startpath, ignored_folders=None, ignored_extensions=None, indent=0
):
    """
    Prints the folder structure starting from the given path.
    Ignored folders and file extensions can be specified.

    :param startpath: The starting path of the directory structure to print.
    :param ignored_folders: A list of folder names to ignore.
    :param ignored_extensions: A list of file extensions to ignore
        (e.g., ['.jpg', '.txt']).
    """
    if ignored_folders is None:
        ignored_folders = []
    if ignored_extensions is None:
        ignored_extensions = []

    for root, dirs, files in os.walk(startpath, topdown=True):
        dirs[:] = [
            d for d in dirs if d not in ignored_folders
        ]  # Modify dirs in place to ignore specified folders
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")

        subindent = " " * 4 * (level + 1)
        for f in files:
            if not any(f.endswith(ext) for ext in ignored_extensions):
                print(f"{subindent}{f}")


# Example usage
start_path = os.getcwd()
ignored_folders = [
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
]  # Example folders to ignore
ignored_extensions = [".pyc", ".log"]  # Example file extensions to ignore

print_folder_structure(start_path, ignored_folders, ignored_extensions)

# %%
