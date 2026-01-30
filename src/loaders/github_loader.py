import os
import shutil
import subprocess
import stat


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clone_github_repo(repo_url, repo_dir="data/github_repo"):
    # Remove old repo safely (Windows fix)
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir, onerror=remove_readonly)

    subprocess.run(
        ["git", "clone", repo_url, repo_dir],
        check=True
    )

    return repo_dir
