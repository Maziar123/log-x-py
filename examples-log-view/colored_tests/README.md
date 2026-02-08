# LogXPy Color Tests

This directory contains tests and examples for LogXPy's color rendering features when viewed with `logxpy-cli-view`.

## Files

- `xx_Color_Methods1.py` - Python script demonstrating all LogXPy color methods
- `xx_Color_Methods1.log` - Generated log file (symlink to `logxpy/examples/`)
- `run_color_test.sh` - Run the Python script and view the output
- `view_color_log.sh` - Quick viewer for the existing log file

## Running the Tests

### Run everything (generate log + view):
```bash
./run_color_test.sh
```

### Just view the existing log:
```bash
# View with colors (default)
./view_color_log.sh

# View with ASCII only
./view_color_log.sh --ascii

# View without colors
./view_color_log.sh --no-color

# Show statistics
./view_color_log.sh --stats

# Live tail the log
./view_color_log.sh --tail
```

## Color Features Demonstrated

1. **Basic Level Colors** - Automatic colors based on log level
2. **Set Foreground Color** - `log.set_foreground()` / `log.reset_foreground()`
3. **Set Background Color** - `log.set_background()` / `log.reset_background()`
4. **Combined Colors** - Foreground + background together
5. **One-Shot Colored Messages** - `log.colored(msg, fg, bg)`
6. **Colored Blocks** - Unicode box-drawing with colors
7. **All Available Colors** - Full color palette demo
8. **Practical Examples** - Real-world usage patterns
9. **Gradient Effect** - Multiple colored messages
10. **Data Type Highlighting** - Different colors for different data types

## Color Palette

Available colors in LogXPy:
- **Basic**: black, red, green, yellow, blue, magenta, cyan, white
- **Extended**: light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan

## LogXPy Color API

```python
from logxpy import log

# Set color for all subsequent logs
log.set_foreground("cyan")
log.set_background("blue")
log.info("This will be cyan on blue")

# Reset to default
log.reset_foreground()
log.reset_background()

# One-shot colored message
log.colored("Important!", foreground="red", background="yellow")

# Method chaining
log.set_foreground("white").set_background("red").error("Critical!")
```
