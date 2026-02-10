Here's a complete **Arch Linux Real-Time File Monitoring Guide** in markdown format—copy and save it as `file-monitor-guide.md`:

```markdown
# Arch Linux Real-Time File Monitoring with Syntax Highlighting (2026)

Complete guide for monitoring file creation and changes with modern syntax highlighting tools.

## Quick Install

```bash
#arch linux
sudo pacman -S tailspin bat inotify-tools lnav watchexec fswatch


#ubuntu
sudo apt install tailspin bat inotify-tools lnav watchexec fswatch
```

---

## Tools Overview

### 1. tailspin (tspin) — Log File Specialist
Automatic highlighting for logs without configuration.

```bash
# Monitor existing file
tspin -f /var/log/nginx/access.log

# Monitor directory
tspin -f /var/log/
```

**Features:** Auto-highlights dates, IPs, UUIDs, URLs, severity levels (ERROR/WARN/INFO), numbers, and paths. Uses `less` pager.

### 2. bat — Code/Config Syntax Highlighting
Like `cat` with Git integration and 200+ language support.

```bash
bat --paging=never --style=numbers,changes config.yaml
```

### 3. lnav — Multi-File Log Analysis
Merged chronological view of multiple logs with SQL support.

```bash
lnav /var/log/*.log
```

### 4. watchexec — Development Workflow
Run commands on file changes (Rust-based, efficient).

```bash
watchexec -e log,json --clear -- bat --paging=never changed-file.log
```

---

## Critical Fix: tailspin Won't Wait for Non-Existent Files

**Problem:** `tspin -f /path/to/file` fails immediately if file doesn't exist.

### Solution A: tail -F + tspin (Simplest)
Preserves highlighting but outputs to stdout (no pager):

```bash
tail -F /var/log/nginx/access.log 2>/dev/null | tspin
```

### Solution B: Wait Loop + tspin (Preserves Pager)
```bash
while [ ! -f /var/log/nginx/access.log ]; do sleep 0.5; done && tspin -f /var/log/nginx/access.log
```

### Solution C: Smart Wrapper Script (Production-Ready)
Handles creation → monitoring → rotation automatically:

```bash
#!/bin/bash
# tspin-wait.sh - Monitor files that don't exist yet

FILE="${1:-/var/log/nginx/access.log}"
DIR=$(dirname "$FILE")

echo "[$(date '+%H:%M:%S')] Waiting for $FILE..."

while true; do
    # Efficient wait using inotify (zero CPU)
    if [ ! -f "$FILE" ]; then
        if command -v inotifywait &> /dev/null; then
            inotifywait -qq -e create "$DIR" 2>/dev/null || sleep 1
        else
            sleep 1
        fi
        continue
    fi
    
    echo "[$(date '+%H:%M:%S')] File detected. Starting monitoring..."
    tspin -f "$FILE"
    
    # If tspin exits, file was deleted/rotated
    echo "[$(date '+%H:%M:%S')] File lost. Waiting for recreation..."
    sleep 0.5
done
```

**Usage:**
```bash
chmod +x tspin-wait.sh
./tspin-wait.sh /var/log/nginx/access.log
```

### Solution D: One-Liner Retry
```bash
until tspin -f /var/log/nginx/access.log 2>/dev/null; do sleep 1; done
```

---

## Practical Recipes

### Monitor New File Creation with Highlighting
Detect when new files are created and display immediately:

```bash
#!/bin/bash
DIR="${1:-.}"

inotifywait -m -r -e create --format '%w%f' "$DIR" | while read file; do
    sleep 0.1  # Wait for write completion
    [ -d "$file" ] && continue
    
    clear
    echo "=== $(date): New file detected ==="
    echo "Path: $file"
    echo "Size: $(stat -c%s "$file") bytes"
    echo "========================================"
    
    # Choose viewer by extension
    case "$file" in
        *.log|*.txt)  tailspin --paging=never "$file" ;;
        *.json|*.yaml|*.yml|*.toml|*.py|*.sh)  
                      bat --paging=never --style=numbers "$file" ;;
        *)            bat --paging=never "$file" ;;
    esac
    
    echo -e "\n>>> Waiting for next file..."
done
```

### Real-Time Development Monitor
Watch for changes in project files:

```bash
# Clear screen and show file with changes highlighted
watchexec -e rs,toml,json -c -r -- bat --paging=never src/main.rs
```

### Systemd Service Log Monitor
Wait for service to start and begin logging:

```bash
sudo systemctl restart nginx && until tspin -f /var/log/nginx/access.log 2>/dev/null; do sleep 1; done
```

---

## Comparison Matrix

| Method | Waits for File | Handles Rotation | Pager Mode | Use Case |
|--------|---------------|------------------|------------|----------|
| `tspin -f` | ❌ No | ❌ No | ✅ Yes | Existing static files |
| `tail -F \| tspin` | ✅ Yes | ✅ Yes | ❌ No | Simple log streaming |
| **Wait + tspin** | ✅ Yes | ❌ No | ✅ Yes | One-time file creation |
| **inotify wrapper** | ✅ Yes | ✅ Yes | ✅ Yes | **Production monitoring** |
| `lnav` | ✅ Yes | ✅ Yes | ✅ Yes | Multiple log files |
| `bat + inotifywait` | ✅ Yes | ❌ No | ❌ No | Code file monitoring |

---

## Pro Tips

1. **True Color Support:** Ensure `COLORTERM=truecolor` is set in your environment for full color support.

2. **less Options:** When in `tspin` pager, use:
   - `Shift+F` - Toggle follow mode (like `tail -f`)
   - `/` - Search
   - `&` - Filter lines
   - `q` - Quit

3. **Custom Highlighting:** Add your own keywords:
   ```bash
   tspin -f app.log --highlight=red:CRITICAL,FAILED --highlight=green:SUCCESS,COMPLETED
   ```

4. **Systemd Integration:** For persistent monitoring across reboots:
   ```bash
   # ~/.config/systemd/user/log-monitor.service
   [Unit]
   Description=Monitor application logs
   
   [Service]
   Type=simple
   ExecStart=/usr/bin/bash -c 'until tspin -f /var/log/app.log 2>/dev/null; do sleep 2; done'
   Restart=always
   
   [Install]
   WantedBy=default.target
   ```

---

## Troubleshooting

**Q: tspin shows "file not found" immediately?**  
A: Use the wait loop or wrapper script above. `tspin -f` requires the file to exist at startup.

**Q: Colors look wrong in tmux/screen?**  
A: Set `export COLORTERM=truecolor` before running tspin.

**Q: bat doesn't show line numbers?**  
A: Add `--style=numbers,changes` or set in `~/.config/bat/config`.

**Q: inotifywait says "No space left on device"?**  
A: Increase inotify limits:
```bash
sudo sysctl fs.inotify.max_user_watches=524288
```
```

**To save this:** Copy the content above and run `cat > file-monitor-guide.md` then paste and press `Ctrl+D`.