import shutil
import os

def clone_repo(source_path, dest_path):
    """
    Clone the repository from the source path to the destination path.
    This copies the repository and its .myscs directory.
    """
    try:
        if not os.path.exists(source_path):
            print(f"Source directory {source_path} does not exist.")
            return
        # Copy the entire source directory to the destination path
        shutil.copytree(source_path, dest_path)
        print(f"Repository cloned from {source_path} to {dest_path}.")
    except Exception as e:
        print(f"Error cloning repository: {str(e)}")
