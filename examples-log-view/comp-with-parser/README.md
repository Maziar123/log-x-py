# LogXPy Comprehensive Example with Color Support

This folder demonstrates the complete logxpy logging pipeline with **foreground/background color support**.

## 🎨 New Color Features

### LogXPy Color API

```python
from logxpy import log

# Method 1: Set foreground color
log.set_foreground("cyan")
log.info("This is cyan text")
log.reset_foreground()

# Method 2: Set background color
log.set_background("yellow")
log.warning("Yellow background warning")
log.reset_background()

# Method 3: Combined colors
log.set_foreground("white").set_background("red")
log.error("White text on red background")
log.reset_foreground().reset_background()

# Method 4: One-shot colored message
log.colored(
    "╔════════════════════════════════════════════════════════════╗\n"
    "║  ⚠️  IMPORTANT WARNING: Yellow background + BLACK font    ║\n"
    "╚════════════════════════════════════════════════════════════╝",
    foreground="black",
    background="yellow"
)
```

## 📁 Files

| File | Purpose |
|------|---------|
| `example_09_comprehensive.py` | Comprehensive logging example with color demos (symlink) |
| `run_and_analyze.sh` | Complete pipeline script |
| `parse_comprehensive.py` | Log parser with line number support |
| `view_tree_colored.py` | **NEW**: Tree viewer with line numbers & colors |
| `view_log_colored.py` | **NEW**: Log viewer showing color hints |
| `view_line_colored.py` | **NEW**: Single line viewer with custom colors |

## 🚀 Running the Pipeline

```bash
./run_and_analyze.sh
```

This runs 6 steps:
1. Clean old logs
2. Run `example_09_comprehensive.py` (generates colored log entries)
3. Check log file
4. Parse & validate with `parse_comprehensive.py`
5. View full tree with `logxpy_cli_view`
6. View tree with line numbers & colors using `view_tree_colored.py`

## 🎨 Colored Lines in Sample

| Line | Foreground | Background | Description |
|------|------------|------------|-------------|
| 108-109 | cyan | - | Cyan foreground demo |
| 111-112 | - | blue | Blue background demo |
| 113 | white | red | Error style (white on red) |
| 114 | yellow | black | Yellow on black |
| 115 | green | black | Green on black |
| 116 | magenta | white | Magenta highlight |
| **117** | **black** | **yellow** | **⚠️ HIGHLIGHT BLOCK** |
| 118-119 | light_cyan | - | Light cyan text |
| 120 | light_cyan | dark_gray | Light cyan on dark gray |

## 📊 Output Example

```
[117] loggerx:info/1  ← BLACK on YELLOW
      ╔══════════════════════════════════════════════════════════════════╗
      ║  ⚠️  IMPORTANT WARNING: Yellow background with BLACK font        ║
      ║     This is a highlighted block for critical attention           ║
      ╚══════════════════════════════════════════════════════════════════╝
```

## 🔧 Viewers

### view_tree_colored.py
Tree view with line numbers and full color blocks:
```bash
python view_tree_colored.py example_09_comprehensive.log
```

### view_log_colored.py
Shows entries with color hints:
```bash
python view_log_colored.py example_09_comprehensive.log
```

### view_line_colored.py
View single line with custom colors:
```bash
python view_line_colored.py <log> <line> <fg> <bg>
python view_line_colored.py app.log 5 red black
```

## 📚 Dependencies

- `colored` - ANSI color support
- `logxpy` - Core logging library
- `logxpy_cli_view` - Tree viewer
- `logxy_log_parser` - Log parser

## ✅ Pipeline Status

All components working:
- ✅ logxpy color methods
- ✅ logxpy_cli_view rendering
- ✅ Line number tracking
- ✅ Full color block highlighting
