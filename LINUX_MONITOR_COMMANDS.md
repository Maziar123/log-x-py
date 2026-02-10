# Linux Real-Time Monitoring Commands

## Single Commands (No Shell Script Needed)

### 1. **watch** - Best for most cases
```bash
# Monitor command every 2 seconds (default)
watch -n 2 'ps aux | grep nginx'

# Monitor with highlighting changes
watch -d 'ls -la /tmp/myfile'

# Monitor with no header
watch -n 1 -t 'df -h /home'

# Monitor system process
watch -n 1 'systemctl status mysql'
```

### 2. **tail -f** - For files
```bash
# Monitor log file in real-time
tail -f /var/log/nginx/access.log

# Monitor with line numbers
tail -f -n 100 /var/log/syslog

# Monitor multiple files
tail -f /var/log/*.log
```

### 3. **while loop** - For custom checks
```bash
# Check if process exists, show real-time updates
while true; do clear; ps aux | grep nginx; sleep 2; done

# Check if file exists with timestamp
while true; do echo "[$(date)] $(ls -la /tmp/myfile 2>&1)"; sleep 1; done

# Monitor disk usage
while true; do clear; df -h /home; sleep 3; done
```

### 4. **journalctl** - For systemd services
```bash
# Follow journal logs in real-time
journalctl -u nginx -f

# Follow with filtering
journalctl -u mysql -f | grep error
```

### 5. **htop / top** - For system monitoring
```bash
# Interactive process monitor
htop

# Or classic top
top
```

## Quick Reference Table

| Command | Use Case | Example |
|---------|----------|---------|
| `watch -n 2 'cmd'` | Any command, auto-refresh | `watch -n 2 'ps aux \| grep nginx'` |
| `tail -f file.log` | Log files | `tail -f /var/log/nginx/access.log` |
| `while true; do cmd; sleep N; done` | Custom checks | `while true; do ls file; sleep 1; done` |
| `journalctl -u service -f` | Systemd services | `journalctl -u nginx -f` |
| `htop` | System resources | `htop` |

## Most Common Use
```bash
watch -n 2 'your_command_here'
```

**Press Ctrl+C to stop any of these commands.**
