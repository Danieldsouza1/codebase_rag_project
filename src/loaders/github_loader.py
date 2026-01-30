import os
import shutil
import subprocess


def clone_github_repo(repo_url, repo_dir="data/github_repo"):
    # Remove old repo if exists
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)

    # Clone repo
    subprocess.run(
        ["git", "clone", repo_url, repo_dir],
        check=True
    )

    return repo_dir
    