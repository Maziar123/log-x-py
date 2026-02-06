# Local-Only Folders Guide

How to keep folders **only on your local machine** (not on GitHub or PyPI).

---

## The Two-File Solution

| File | Purpose | Affects |
|------|---------|---------|
| `.gitignore` | Excludes from git commits | GitHub, GitLab, etc. |
| `MANIFEST.in` | Excludes from package | PyPI, pip installs |

---

## Common Local-Only Folder Patterns

### 1. Personal Notes & Configuration
```gitignore
# .gitignore
.local/           # Personal scripts/tools
private/          # Private notes
personal/         # Personal config
notes/            # Working notes
config.local.yaml # Local overrides
```

### 2. Large Data Files
```gitignore
# .gitignore
data/             # Large datasets
datasets/         # ML training data
*.csv             # Data files
*.parquet         # Columnar data
*.db              # SQLite databases
*.sqlite          # SQLite databases
```

### 3. Experiments & Drafts
```gitignore
# .gitignore
experiments/      # Experimental code
prototypes/       # Quick prototypes
drafts/           # Draft work
scratch/          # Scratch work
sandbox/          # Testing area
```

---

## How It Works

### Scenario 1: Completely Local Folder

```bash
# 1. Create folder locally
mkdir my_experiments
echo "test" > my_experiments/test.py

# 2. Add to .gitignore (root of project)
echo "my_experiments/" >> .gitignore

# 3. Add to MANIFEST.in (in logxpy/ folder)
echo "global-exclude my_experiments/*" >> logxpy/MANIFEST.in
```

**Result:**
- ✅ Exists locally
- ❌ Not on GitHub
- ❌ Not in PyPI package

---

### Scenario 2: Data Folder (Large Files)

```bash
# 1. Create data folder
mkdir data
curl -o data/large_dataset.csv "https://example.com/data.csv"  # 500MB

# 2. Already covered by .gitignore (data/ is in the template)
# 3. Already covered by MANIFEST.in (*.csv excluded)
```

**Result:**
- ✅ Exists locally
- ❌ Not committed to git
- ❌ Not uploaded to PyPI

---

### Scenario 3: Local Configuration

```bash
# 1. Create local config from template
cp config.yaml config.local.yaml
# Edit config.local.yaml with your API keys, paths, etc.

# 2. Already covered by .gitignore (config.local.yaml excluded)
```

**Result:**
- ✅ Your local config works
- ❌ Your secrets don't leak to GitHub
- ❌ Not in PyPI package

---

## Verifying Exclusions

### Check Git (GitHub)
```bash
# See what git is ignoring
git status --ignored

# Check if a specific file is tracked
git check-ignore -v my_folder/file.txt

# See what would be committed
git ls-files
```

### Check PyPI Package
```bash
cd logxpy

# Build package
python setup.py sdist

# See what's inside the tarball
tar -tzf dist/logxpy-*.tar.gz | less

# Check if your folder is excluded
tar -tzf dist/logxpy-*.tar.gz | grep my_folder
# (should return nothing if excluded)
```

---

## Template: Add New Local Folder

### Step 1: Add to `.gitignore`
```gitignore
# Local-only: my_folder
my_folder/
```

### Step 2: Add to `logxpy/MANIFEST.in`
```
# Exclude from PyPI
global-exclude my_folder/*
```

### Step 3: Create locally
```bash
mkdir my_folder
# Put your files here - they stay local only!
```

---

## Current Local-Only Folders (Configured)

These folders are already set up to be local-only:

| Folder | Purpose |
|--------|---------|
| `.local/` | Personal scripts/tools |
| `private/` | Private notes/files |
| `personal/` | Personal configuration |
| `notes/` | Working notes |
| `experiments/` | Experimental code |
| `prototypes/` | Quick prototypes |
| `drafts/` | Draft work |
| `.work/` | Working directory |
| `workspace/` | Workspace files |
| `sandbox/` | Testing sandbox |
| `data/` | Large datasets |
| `datasets/` | ML/data files |

---

## Important Notes

1. **Git is retroactive**: Adding to `.gitignore` doesn't remove already-tracked files
   ```bash
   # Remove already-tracked files from git (keep locally)
   git rm -r --cached my_folder
   git commit -m "Remove my_folder from tracking"
   ```

2. **PyPI uses MANIFEST.in**: Without it, `setup.py` might include everything

3. **Both files needed**: `.gitignore` ≠ `MANIFEST.in` - they serve different purposes

4. **Test before publishing**: Always verify with `tar -tzf dist/*.tar.gz`
