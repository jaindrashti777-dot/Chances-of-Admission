import subprocess
import os

def run(cmd, env=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    if res.returncode != 0:
        print(f"Error running '{cmd}': {res.stderr}")
    return res.stdout.strip()

commits_raw = run("git log --format=\"%H|%s\" --reverse")
commits = [c for c in commits_raw.split("\n") if c.strip()]

mapping = {
    "Initial project setup": "chore: initial project setup",
    "Backend foundation": "feat(backend): setup fastapi foundation",
    "Database layer": "feat(db): implement database schema and ORM",
    "ML preprocessing": "feat(ml): add data preprocessing pipeline",
    "Model training": "feat(ml): implement xgboost model training",
    "Prediction API": "feat(api): create admission prediction endpoint",
    "Recommendation engine": "feat(api): add college recommendation engine",
    "Frontend foundation": "feat(ui): setup react frontend and routing",
    "Dashboard UI": "feat(ui): build interactive prediction dashboard",
    "Deployment": "chore(devops): configure docker and deployment services",
    "Documentation": "docs: add comprehensive project documentation",
    "Refactor: Engineering architecture and frontend UX modernization": "refactor(ui): modernize frontend UX and components",
    "Refactor: Restructure ML pipeline directories and untrack generated outputs": "refactor(ml): restructure pipeline directories",
    "Refactor: rename inference to prediction, move pagination to api layer": "refactor(backend): standardize domain names",
    "Refactor: migrate frontend to feature-based architecture and remove AI boilerplate": "refactor(ui): migrate to feature-based frontend architecture",
    "Refactor: Add standard ML modules for evaluation, pipelines, and experiments": "refactor(ml): add evaluation and experiment modules",
    "Refactor: Update backend prediction modules to clearer domain names and add engineering decisions doc": "refactor(backend): update prediction domain terminology",
    "feat: improve frontend UX, remove generic components and add actionable model insights": "feat(ui): improve results UX with actionable insights",
}

print("Switching to an orphan branch...")
run("git checkout --orphan rewrite_history")
run("git rm -rf .")

env = os.environ.copy()

for i, commit in enumerate(commits):
    parts = commit.split("|", 1)
    if len(parts) != 2:
        continue
    hash_val, msg = parts
    
    new_msg = mapping.get(msg, msg)
    if new_msg.startswith("Refactor: "):
        new_msg = "refactor: " + new_msg[10:]
    new_msg = new_msg.replace('"', '\\"')
        
    print(f"Replaying {hash_val[:7]}: {new_msg}")
    
    author_name = run(f"git log -1 --format=\"%an\" {hash_val}")
    author_email = run(f"git log -1 --format=\"%ae\" {hash_val}")
    author_date = run(f"git log -1 --format=\"%ad\" {hash_val}")
    
    # Pass environment variables safely through Python's env dictionary
    custom_env = env.copy()
    custom_env["GIT_AUTHOR_NAME"] = author_name
    custom_env["GIT_AUTHOR_EMAIL"] = author_email
    custom_env["GIT_AUTHOR_DATE"] = author_date
    custom_env["GIT_COMMITTER_NAME"] = author_name
    custom_env["GIT_COMMITTER_EMAIL"] = author_email
    custom_env["GIT_COMMITTER_DATE"] = author_date
    
    run(f"git read-tree {hash_val}")
    run(f"git checkout -- .")
    run(f"git add -A")
    
    commit_cmd = f'git commit --allow-empty -m "{new_msg}"'
    run(commit_cmd, env=custom_env)

print("Rewriting complete. Moving main to new history.")
run("git branch -f main rewrite_history")
run("git checkout main")
run("git branch -D rewrite_history")
run("git push -f origin main")
