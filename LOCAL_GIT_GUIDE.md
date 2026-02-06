# Local Git vs GitHub - Guide

How to keep files in **local git** (tracked, versioned) but **never push to GitHub**.

---

## Quick Comparison

| Approach | Local Git | GitHub | Best For |
|----------|:---------:|:------:|----------|
| **Pre-push Hook** | ✅ Tracked | ❌ Blocked | Secrets, credentials |
| **Local-Only Branch** | ✅ Commits | ❌ Never pushed | Personal experiments |
| **Git Worktree** | ✅ Separate | ❌ Selective | Isolated development |
| **Sparse Push** | ✅ Partial | ⚠️ Partial | Large files |

---

## Option 1: Pre-Push Hook ⭐ (Recommended)

**Use case:** Secrets, API keys, local configs that you want versioned locally but never leaked.

### Setup

```bash
# 1. Install the hook
cp git-hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push

# 2. Edit patterns in .git/hooks/pre-push to match your local files
```

### How It Works

```bash
# Add and commit locally (works fine)
git add local/config.yaml
git commit -m "Add local config"

# Try to push (BLOCKED!)
git push origin main
# ❌ PUSH BLOCKED: Local-only files detected!
#   • local/config.yaml
```

### Bypass (Emergency Only)

```bash
git push --no-verify  # Force push (DANGER!)
```

---

## Option 2: Local-Only Branch

**Use case:** Personal experiments, notes, scripts that you want tracked but never shared.

### Setup

```bash
# 1. Create a local branch that tracks main
git checkout -b local/personal main

# 2. Add your personal files
echo "my notes" > personal/notes.md
git add personal/
git commit -m "Personal notes"

# 3. Configure to NEVER push this branch
git config branch.local/personal.remote ""
git config branch.local/personal.merge ""
```

### Workflow

```bash
# Work on main, merge updates to personal
git checkout main
# ... work ...
git commit -am "Work done"

git checkout local/personal
git merge main  # Get latest changes

# Push main to GitHub
git checkout main
git push origin main  # ✅ Only main goes to GitHub

# Personal branch stays local
git checkout local/personal
# ... personal work ...
git commit -am "Personal updates"
# No push command - branch is local-only!
```

### Prevent Accidental Push

```bash
# Block pushing local/* branches
git config --local remote.origin.push "refs/heads/main:refs/heads/main"
```

---

## Option 3: Git Worktree (Advanced)

**Use case:** Completely separate working directories - one for GitHub, one for local.

### Setup

```bash
# 1. Main worktree (for GitHub)
# (Your current directory)

# 2. Create local-only worktree
git worktree add ../log-x-py-local local/personal

# 3. In the local worktree, add files freely
cd ../log-x-py-local
mkdir secrets
echo "API_KEY=xxx" > secrets/keys
git add secrets/
git commit -m "Add secrets"
```

### Structure

```
projects/
├── log-x-py/           # Main directory → pushes to GitHub
│   └── (public files only)
└── log-x-py-local/     # Local worktree → never pushed
    └── (private files allowed)
```

---

## Option 4: Skip Worktree (Not Recommended)

**Note:** This doesn't prevent pushing, but keeps local modifications from being committed.

```bash
# Mark file as "don't track changes"
git update-index --skip-worktree local/config.yaml

# Make changes freely
echo "SECRET=123" >> local/config.yaml

# Won't show in git status, but still in repo!
```

**Problem:** File is still in the repo and will be pushed if it was ever committed.

---

## Option 5: Separate Git Config

Create a completely separate git repository for local files that references the main project:

```bash
# 1. Main project (GitHub)
cd /projects/log-x-py

# 2. Local project (separate git repo)
mkdir /projects/log-x-py-private
cd /projects/log-x-py-private
git init

# 3. Symlink or copy what you need
ln -s /projects/log-x-py/logxpy ./logxpy
ln -s /projects/log-x-py/README.md ./README.md

# 4. Add local-only files
echo "secrets" > .secrets
git add .secrets
git commit -m "Local secrets"
```

---

## Recommended Setup for This Project

### Step 1: Create Local Directories

```bash
# Create local-only directories
mkdir -p local/secrets
mkdir -p local/experiments
mkdir -p local/notes
```

### Step 2: Install Pre-Push Hook

```bash
cp git-hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

### Step 3: Configure Local Patterns

Edit `.git/hooks/pre-push` and add your patterns:

```bash
LOCAL_ONLY_PATTERNS=(
    "local/"           # All local/ directory
    "private/"
    "*.local.json"     # Files ending in .local.json
    "*.secret"
    "credentials.yaml"
)
```

### Step 4: Use It

```bash
# Add local secrets
echo "API_KEY=xxx" > local/secrets/api.key
git add local/
git commit -m "Add API keys"

# Push to GitHub (BLOCKED if local/ is in patterns!)
git push origin main
# ❌ Error: Local-only files detected!

# Remove from commit
git reset HEAD local/secrets/api.key

# Keep locally but don't commit
git stash push local/secrets/api.key
# Or just leave uncommitted
```

---

## Testing

### Test Pre-Push Hook

```bash
# Create test file
echo "test" > local/test.txt
git add local/test.txt
git commit -m "Test local file"

# Try pushing (should fail)
git push --dry-run  # Or actual push

# Cleanup
git reset HEAD~1
rm local/test.txt
```

### Verify What's Being Pushed

```bash
# See what would be pushed
git log --oneline @{u}..HEAD
git diff --stat @{u}..HEAD

# Check for local files
git diff --name-only @{u}..HEAD | grep "^local/"
```

---

## Summary

| Method | Difficulty | Safety | Flexibility |
|--------|:----------:|:------:|:-----------:|
| Pre-push Hook | Easy | ⭐⭐⭐ High | Medium |
| Local Branch | Medium | ⭐⭐⭐ High | High |
| Git Worktree | Hard | ⭐⭐⭐ High | Very High |
| Separate Repo | Medium | ⭐⭐⭐ High | Medium |

**Recommendation:** Use **Pre-push Hook** for most cases. It's simple, effective, and prevents accidents.
