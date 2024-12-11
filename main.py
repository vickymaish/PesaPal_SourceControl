import argparse
from repoinit import initialize_repo
from staging import stage_file
from commit_change import commit, view_commit_history, merge  # Import the commit and log functions
from branching import create_branch, switch_branch  # Import branch-related functions
from diff import compare_branches  # Import the compare_branches function for diffing
from clone import clone_repo

def main():
    parser = argparse.ArgumentParser(description="PesaPal Simple version control system.")
    subparsers = parser.add_subparsers(dest="command")

    # 'init' command
    init_parser = subparsers.add_parser("init", help="Initialize a new repository.")
    init_parser.set_defaults(func=initialize_repo)

    # 'add' command
    add_parser = subparsers.add_parser("add", help="Stage a file.")
    add_parser.add_argument("file_path", help="Path to the file to be staged.")
    add_parser.set_defaults(func=stage_file)

    # 'commit' command
    commit_parser = subparsers.add_parser("commit", help="Commit staged changes.")
    commit_parser.add_argument("commit_message", help="Commit message.")
    commit_parser.set_defaults(func=commit)

    # 'log' command
    log_parser = subparsers.add_parser("log", help="View commit history.")
    log_parser.set_defaults(func=view_commit_history)

    # 'branch' command for creating a new branch
    branch_parser = subparsers.add_parser("branch", help="Create a new branch.")
    branch_parser.add_argument("branch_name", help="Name of the branch to create.")
    branch_parser.set_defaults(func=create_branch)

    # 'switch' command for switching branches
    switch_parser = subparsers.add_parser("switch", help="Switch to an existing branch.")
    switch_parser.add_argument("branch_name", help="Name of the branch to switch to.")
    switch_parser.set_defaults(func=switch_branch)

    # 'merge' command for merging branches
    merge_parser = subparsers.add_parser("merge", help="Merge the current branch with another branch.")
    merge_parser.add_argument("branch_name", help="Name of the branch to merge.")
    merge_parser.set_defaults(func=merge)

    # 'diff' command for comparing two branches
    diff_parser = subparsers.add_parser("diff", help="Compare two branches to see the differences.")
    diff_parser.add_argument("branch1", help="First branch to compare.")
    diff_parser.add_argument("branch2", help="Second branch to compare.")
    diff_parser.set_defaults(func=compare_branches)


    # 'clone' command for cloning repositories
    clone_parser = subparsers.add_parser("clone", help="Clone a repository.")
    clone_parser.add_argument("source_path", help="Path to the source repository.")
    clone_parser.add_argument("dest_path", help="Path where the repository will be cloned.")
    clone_parser.set_defaults(func=clone_repo)

    args = parser.parse_args()
    if args.command:
        # Check if a file path is provided for 'add'
        if args.command == "add":
            args.func(args.file_path)
        # Check if a commit message is provided for 'commit'
        elif args.command == "commit":
            args.func(args.commit_message)
        # Check for branch and switch functionality
        elif args.command == "branch":
            args.func(args.branch_name)
        elif args.command == "switch":
            args.func(args.branch_name)
        # Check for the merge functionality
        elif args.command == "merge":
            args.func(args.branch_name)
        # Check for diff functionality
        elif args.command == "diff":
            args.func(args.branch1, args.branch2)

        elif args.command =="clone":
            args.func(args.source_path, args.dest_path)
        else:
            args.func()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
