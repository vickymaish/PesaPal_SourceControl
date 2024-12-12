import os
import json
from rich.console import Console
from rich.table import Table
import time

console = Console()

def compare_branches(branch1, branch2):
    """
    Compare the commit history of two branches and display the differences.
    """
    # Get the latest commit hashes for both branches
    branch1_commit_hash = get_commit_hash_for_branch(branch1)
    branch2_commit_hash = get_commit_hash_for_branch(branch2)

    if not branch1_commit_hash or not branch2_commit_hash:
        console.print(f"[bold red]Error: One or both branches do not exist.[/bold red]")
        return

    # Get commit history for both branches
    branch1_commits = get_commit_history(branch1_commit_hash)
    branch2_commits = get_commit_history(branch2_commit_hash)

    if not branch1_commits or not branch2_commits:
        console.print("[bold yellow]No commits found for one or both branches.[/bold yellow]")
        return

    # Initialize a table for output
    table = Table(title=f"Diff between {branch1} and {branch2}")
    table.add_column("Commit Hash", style="cyan")
    table.add_column("Message", style="magenta")
    table.add_column("Timestamp", style="dim")

    # Find the common commits and the differing commits
    common_commits = set(commit['commit_hash'] for commit in branch1_commits) & set(commit['commit_hash'] for commit in branch2_commits)
    diff_commits_branch1 = set(commit['commit_hash'] for commit in branch1_commits) - common_commits
    diff_commits_branch2 = set(commit['commit_hash'] for commit in branch2_commits) - common_commits

    # Display common commits
    if common_commits:
        console.print("[bold green]Common commits between the branches:[/bold green]")
        for commit_hash in common_commits:
            table.add_row(commit_hash[:7], "[green]Common Commit[/green]", "N/A")

    # Display commits only in branch1
    if diff_commits_branch1:
        console.print(f"[bold red]Commits unique to {branch1}:[/bold red]")
        for commit in branch1_commits:
            if commit['commit_hash'] in diff_commits_branch1:
                formatted_timestamp = time.ctime(commit['timestamp'])  # Format the timestamp
                table.add_row(commit['commit_hash'][:7], f"[red]Only in {branch1}[/red]", formatted_timestamp)

    # Display commits only in branch2
    if diff_commits_branch2:
        console.print(f"[bold blue]Commits unique to {branch2}:[/bold blue]")
        for commit in branch2_commits:
            if commit['commit_hash'] in diff_commits_branch2:
                formatted_timestamp = time.ctime(commit['timestamp'])  # Format the timestamp
                table.add_row(commit['commit_hash'][:7], f"[blue]Only in {branch2}[/blue]", formatted_timestamp)

    # Show the table
    console.print(table)


def get_commit_hash_for_branch(branch_name):
    """
    Get the latest commit hash for the branch.
    """
    branch_path = f".myscs/refs/heads/{branch_name}"
    if os.path.exists(branch_path):
        with open(branch_path, "r") as branch_file:
            return branch_file.read().strip()
    return None


def get_commit_history(commit_hash):
    """
    Recursively fetch the commit history for a given commit hash.
    Now returns a list of commit details, not just commit hashes.
    """
    commit_history = []
    while commit_hash:
        commit_path = f".myscs/objects/{commit_hash}"
        if not os.path.exists(commit_path):
            break
        with open(commit_path, "r") as commit_file:
            commit_data = json.load(commit_file)
            commit_history.append({
                "commit_hash": commit_hash,
                "commit_message": commit_data.get("commit_message", ""),
                "timestamp": commit_data.get("timestamp", ""),
                "parent_commit": commit_data.get("parent_commit", None),
            })
            commit_hash = commit_data.get("parent_commit")
    return commit_history
