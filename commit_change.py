import os
import json
import hashlib
import time
import logging
from rich.console import Console
from rich.table import Table
from rich.text import Text


# Initialize rich console for output
console = Console()

# Configure logging
logging.basicConfig(
    filename="myscs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def commit(commit_message):
    """
    Commit the staged files to the repository with a given commit message.
    """
    index_path = ".myscs/index"

    # Step 1: Check if the index is empty (no staged files)
    if not os.path.exists(index_path) or os.path.getsize(index_path) == 0:
        print("No files staged for commit.")
        logging.warning("Commit attempt with no staged files.")
        return

    # Step 2: Read staged files from the index
    staged_files = []
    try:
        with open(index_path, "r") as index_file:
            for line in index_file:
                file_path, file_hash = line.strip().split()
                staged_files.append((file_path, file_hash))
    except Exception as e:
        print(f"Error reading index file: {str(e)}")
        logging.error(f"Error reading index file: {str(e)}")
        return

    # Step 3: Validate staged files
    for file_path, file_hash in staged_files:
        if not os.path.exists(file_path):
            print(f"Error: Staged file '{file_path}' does not exist.")
            logging.error(f"Staged file '{file_path}' missing during commit.")
            return
        # Verify file hash
        hasher = hashlib.sha1()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            if hasher.hexdigest() != file_hash:
                print(f"Error: File '{file_path}' has been modified since staging.")
                logging.error(f"File '{file_path}' hash mismatch during commit.")
                return
        except Exception as e:
            print(f"Error reading staged file '{file_path}': {str(e)}")
            logging.error(f"Error reading staged file '{file_path}': {str(e)}")
            return

    # Step 4: Create the commit object data
    commit_data = {
        "commit_message": commit_message,
        "timestamp": time.time(),
        "parent_commit": get_current_commit_hash(),  # Reference to the parent commit
        "files": staged_files
    }
    commit_data_str = json.dumps(commit_data, indent=4)

    # Step 5: Calculate the hash for the commit object
    commit_hash = hashlib.sha1(commit_data_str.encode('utf-8')).hexdigest()

    # Step 6: Save the commit object to the object directory
    commit_path = f".myscs/objects/{commit_hash}"
    try:
        with open(commit_path, "w") as commit_file:
            commit_file.write(commit_data_str)
        logging.info(f"Commit object created with hash {commit_hash}")
    except Exception as e:
        print(f"Error saving commit object: {str(e)}")
        logging.error(f"Error saving commit object: {str(e)}")
        return

    # Step 7: Update HEAD to point to the new commit
    try:
        with open(".myscs/HEAD", "w") as head_file:
            head_file.write(f"ref: refs/heads/main\n{commit_hash}")
        logging.info("HEAD updated to new commit.")
    except Exception as e:
        print(f"Error updating HEAD: {str(e)}")
        logging.error(f"Error updating HEAD: {str(e)}")
        return

    # Step 8: Provide feedback
    print(f"Commit successful. Commit hash: {commit_hash}")
    logging.info("Commit completed successfully.")
def get_current_commit_hash():
    """
    Get the current commit hash from the HEAD file.
    Returns None if HEAD is not present or contains no commit hash.
    """
    head_path = ".myscs/HEAD"
    try:
        if os.path.exists(head_path):
            with open(head_path, "r") as head_file:
                content = head_file.read().strip()
                
                # Handle case where HEAD contains a reference and a hash
                if "ref: refs/heads/main" in content:
                    lines = content.splitlines()  # Split into lines
                    if len(lines) > 1:  # If there's a second line, assume it's the hash
                        return lines[1]
                    else:
                        logging.error("HEAD file reference found but no commit hash.")
                        return None

                # Handle case where HEAD directly contains a commit hash
                elif len(content) == 40:  # SHA-1 hashes are 40 characters long
                    return content

                else:
                    logging.warning("Unrecognized HEAD file format.")
                    return None

    except Exception as e:
        logging.error(f"Error reading HEAD file: {str(e)}")
    return None  # Return None if no valid commit hash is found

def view_commit_history():
    """
    Display the commit history, starting from the latest commit (HEAD).
    """
    head_path = ".myscs/HEAD"
    if not os.path.exists(head_path):
        console.print("[bold red]No commits found. Repository is empty.[/bold red]")
        logging.warning("Attempted to view commit history, but no HEAD found.")
        return

    # Read HEAD to get the latest commit hash
    with open(head_path, "r") as head_file:
        head_content = head_file.read().strip()

    if "ref: refs/heads/main" not in head_content:
        console.print("[bold red]Invalid HEAD reference.[/bold red]")
        logging.error("HEAD does not point to a valid commit.")
        return

    current_commit_hash = head_content.split("\n")[-1]

    # Create a table to display commit history
    table = Table(title="Commit History", style="bold green")
    table.add_column("Commit Hash", justify="right", style="cyan", no_wrap=True)
    table.add_column("Message", style="magenta")
    table.add_column("Timestamp", style="dim")

    # Traverse commit history
    while current_commit_hash:
        commit_path = f".myscs/objects/{current_commit_hash}"
        if not os.path.exists(commit_path):
            console.print(f"[bold red]Commit object {current_commit_hash} not found.[/bold red]")
            logging.error(f"Commit object {current_commit_hash} not found.")
            break

        # Read and display commit data
        with open(commit_path, "r") as commit_file:
            commit_data = json.load(commit_file)
            commit_timestamp = time.ctime(commit_data['timestamp'])
            table.add_row(current_commit_hash[:7], commit_data['commit_message'], commit_timestamp)

        # Get the parent commit hash
        current_commit_hash = commit_data.get("parent_commit")

    # Display the table
    console.print(table)
   

def merge(target_branch):
    """
    Merge the current branch with the target branch.
    If the branches have diverged, a three-way merge is performed.
    """
    current_branch = get_current_branch()  # Get the current active branch
    if current_branch == target_branch:
        # Show warning in yellow if the target is the same as the current branch
        console.print(Text(f"You are already on the target branch '{target_branch}'.", style="yellow"))
        return

    target_commit_hash = get_commit_hash_for_branch(target_branch)
    if not target_commit_hash:
        # Show error in red if the target branch doesn't exist
        console.print(Text(f"Error: Branch '{target_branch}' does not exist.", style="bold red"))
        return

    # Perform a simple merge or three-way merge
    merge_result = perform_merge(current_branch, target_branch)
    if merge_result:
        # Show success in green if the merge is successful
        console.print(Text(f"Merge successful. Merged {target_branch} into {current_branch}.", style="bold green"))
    else:
        # Show error in red if merge conflicts occur
        console.print(Text(f"Merge conflict detected. Unable to merge {target_branch} into {current_branch}.", style="bold red"))

def get_commit_hash_for_branch(branch_name):
    """
    Get the commit hash for the specified branch from the .myscs/refs/heads directory.
    """
    branch_path = f".myscs/refs/heads/{branch_name}"
    if os.path.exists(branch_path):
        with open(branch_path, "r") as branch_file:
            return branch_file.read().strip()
    return None

def perform_merge(current_branch, target_branch):
    """
    Perform the merge operation.
    This will check for diverged commits and attempt to merge them.
    For now, we assume the merge always succeeds.
    """
    # Here, you would check if the branches have diverged and implement the merge logic.
    # For now, we're assuming a simple merge without checking for conflicts.
    
    return True  # Simplified for demonstration purposes

def get_current_branch():
    """
    Retrieve the current branch from HEAD or refs/heads.
    """
    head_path = ".myscs/HEAD"
    if os.path.exists(head_path):
        with open(head_path, "r") as head_file:
            content = head_file.read().strip()
            if content.startswith("ref: refs/heads/"):
                return content.split('/')[-1]
    return None

if __name__ == "__main__":
    # Example usage
    commit("Initial commit")
    view_commit_history()

