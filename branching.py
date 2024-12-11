import os
import logging
from rich.console import Console
from commit_change import get_current_commit_hash  # Import this from commit_change.py

# Initialize Rich console
console = Console()

def create_branch(branch_name):
    """
    Create a new branch in the repository and switch to it.
    """
    branches_dir = ".myscs/refs/heads"
    if not os.path.exists(branches_dir):
        os.makedirs(branches_dir)

    # Check if the branch already exists
    branch_path = os.path.join(branches_dir, branch_name)
    if os.path.exists(branch_path):
        console.print(f"[bold red]Error:[/bold red] Branch '{branch_name}' already exists.")
        logging.warning(f"Attempt to create existing branch '{branch_name}'.")
        return

    # Create a new branch by pointing it to the current commit (HEAD)
    current_commit_hash = get_current_commit_hash()  # Fetch the current commit
    if current_commit_hash:
        with open(branch_path, 'w') as branch_file:
            branch_file.write(current_commit_hash)
        console.print(f"[bold green]Branch '{branch_name}' created successfully.[/bold green]")
        logging.info(f"Branch '{branch_name}' created and points to commit {current_commit_hash}.")
    else:
        console.print(f"[bold yellow]Warning:[/bold yellow] Cannot create branch '{branch_name}' - No commit history found.")
        logging.error(f"Failed to create branch '{branch_name}' - No commit history.")

def switch_branch(branch_name):
    """
    Switch to an existing branch.
    """
    branch_path = f".myscs/refs/heads/{branch_name}"

    if not os.path.exists(branch_path):
        console.print(f"[bold red]Error:[/bold red] Branch '{branch_name}' does not exist.")
        logging.warning(f"Attempt to switch to non-existing branch '{branch_name}'.")
        return

    # Read the commit hash from the branch file
    with open(branch_path, "r") as branch_file:
        commit_hash = branch_file.read().strip()

    # Update the HEAD file to point to the new branch
    with open(".myscs/HEAD", "w") as head_file:
        head_file.write(f"ref: refs/heads/{branch_name}\n{commit_hash}")

    console.print(f"[bold green]Switched to branch:[/bold green] [cyan]{branch_name}[/cyan] (Commit: [magenta]{commit_hash}[/magenta]).")
    logging.info(f"Switched to branch '{branch_name}' (Commit: {commit_hash}).")
