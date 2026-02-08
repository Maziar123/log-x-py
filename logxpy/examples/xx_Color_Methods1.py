#!/usr/bin/env python3
"""
Color Methods Example for LogXPy

This example demonstrates all color and style methods in LogXPy
that create colored blocks or lines when viewed with logxpy-cli-view.

Run this script to generate a log file, then view it with:
    logxpy-view xx_Color_Methods1.log
"""

from logxpy import log, to_file
from pathlib import Path

# Set output file
log_file = Path(__file__).with_suffix('.log')
to_file(open(log_file, 'w'))

def main():
    print(f"Generating colored log examples to {log_file}")

    # === 1. BASIC LEVEL COLORS (Automatic) ===
    log.info("=" * 60)
    log.info("1. BASIC LEVEL COLORS (Automatic)")
    log.info("=" * 60)

    log.debug("This is a DEBUG message - renders in gray")
    log.info("This is an INFO message - renders in white")
    log.success("This is a SUCCESS message - renders in bright green")
    log.note("This is a NOTE message - renders in yellow")
    log.warning("This is a WARNING message - renders in bright yellow")
    log.error("This is an ERROR message - renders in red")
    log.critical("This is a CRITICAL message - renders in bright red with background")

    # === 2. SET FOREGROUND COLOR ===
    log.info("=" * 60)
    log.info("2. SET FOREGROUND COLOR")
    log.info("=" * 60)

    log.set_foreground("cyan")
    log.info("Cyan foreground text")
    log.debug("Debug message with cyan foreground")
    log.success("Success message with cyan foreground")
    log.reset_foreground()

    log.set_foreground("green")
    log.info("Green foreground text")
    log.reset_foreground()

    log.set_foreground("yellow")
    log.info("Yellow foreground text")
    log.reset_foreground()

    log.set_foreground("magenta")
    log.info("Magenta foreground text")
    log.reset_foreground()

    log.set_foreground("red")
    log.info("Red foreground text")
    log.reset_foreground()

    # === 3. SET BACKGROUND COLOR ===
    log.info("=" * 60)
    log.info("3. SET BACKGROUND COLOR")
    log.info("=" * 60)

    log.set_background("yellow")
    log.info("Yellow background - warning style")
    log.reset_background()

    log.set_background("red")
    log.error("Red background - error style")
    log.reset_background()

    log.set_background("blue")
    log.info("Blue background - info style")
    log.reset_background()

    # === 4. COMBINED FOREGROUND AND BACKGROUND ===
    log.info("=" * 60)
    log.info("4. COMBINED FOREGROUND AND BACKGROUND")
    log.info("=" * 60)

    log.set_foreground("white").set_background("red")
    log.error("White on red - critical error style")
    log.reset_foreground().reset_background()

    log.set_foreground("black").set_background("yellow")
    log.warning("Black on yellow - highlight style")
    log.reset_foreground().reset_background()

    log.set_foreground("cyan").set_background("blue")
    log.info("Cyan on blue - info highlight")
    log.reset_foreground().reset_background()

    # === 5. ONE-SHOT COLORED MESSAGES ===
    log.info("=" * 60)
    log.info("5. ONE-SHOT COLORED MESSAGES (colored method)")
    log.info("=" * 60)

    log.colored("Important message in red", foreground="red")
    log.colored("Success message in green", foreground="green")
    log.colored("Warning message in yellow", foreground="yellow")

    # With background
    log.colored(
        "⚠️  WARNING with yellow background",
        foreground="black",
        background="yellow"
    )

    log.colored(
        "❌ ERROR with red background",
        foreground="white",
        background="red"
    )

    log.colored(
        "✅ SUCCESS with green background",
        foreground="white",
        background="green"
    )

    # === 6. COLORED BLOCKS (Unicode Box Drawing) ===
    log.info("=" * 60)
    log.info("6. COLORED BLOCKS (Unicode Box Drawing)")
    log.info("=" * 60)

    # Warning block
    log.colored(
        "╔════════════════════════════════════════════════════════════╗\n"
        "║  ⚠️  WARNING - IMPORTANT NOTICE                               ║\n"
        "║                                                                ║\n"
        "║  This is a highlighted warning block using Unicode characters   ║\n"
        "║  Yellow background with black text for maximum visibility     ║\n"
        "╚════════════════════════════════════════════════════════════╝",
        foreground="black",
        background="yellow"
    )

    # Error block
    log.colored(
        "╔════════════════════════════════════════════════════════════╗\n"
        "║  ❌ ERROR - CRITICAL FAILURE                                     ║\n"
        "║                                                                ║\n"
        "║  This is an error block with red background                     ║\n"
        "║  White text on red background for critical issues              ║\n"
        "╚════════════════════════════════════════════════════════════╝",
        foreground="white",
        background="red"
    )

    # Success block
    log.colored(
        "╔════════════════════════════════════════════════════════════╗\n"
        "║  ✅ SUCCESS - OPERATION COMPLETED                               ║\n"
        "║                                                                ║\n"
        "║  This is a success block with green background                  ║\n"
        "║  White text on green background for positive results          ║\n"
        "╚════════════════════════════════════════════════════════════╝",
        foreground="white",
        background="green"
    )

    # Info block (cyan)
    log.colored(
        "╔════════════════════════════════════════════════════════════╗\n"
        "║  ℹ️  INFO - INFORMATION                                          ║\n"
        "║                                                                ║\n"
        "║  This is an info block with cyan background                      ║\n"
        "║  Black text on cyan background for informational content        ║\n"
        "╚════════════════════════════════════════════════════════════╝",
        foreground="black",
        background="cyan"
    )

    # === 7. ALL AVAILABLE COLORS DEMO ===
    log.info("=" * 60)
    log.info("7. ALL AVAILABLE COLORS DEMO")
    log.info("=" * 60)

    colors = [
        "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
        "light_gray", "dark_gray", "light_red", "light_green", "light_blue",
        "light_yellow", "light_magenta", "light_cyan"
    ]

    for color in colors:
        log.colored(f"  → {color:12s} text example  ←", foreground=color)

    # === 8. PRACTICAL EXAMPLES ===
    log.info("=" * 60)
    log.info("8. PRACTICAL EXAMPLES")
    log.info("=" * 60)

    # Database query highlight
    log.colored(
        "💾 Database: Slow query detected (>5 seconds)",
        foreground="cyan"
    )

    # Payment success
    log.colored(
        "💳 Payment: $99.99 payment completed successfully",
        foreground="green"
    )

    # Authentication failure
    log.colored(
        "🔐 Auth: Invalid credentials - access denied",
        foreground="white",
        background="red"
    )

    # API rate limit
    log.colored(
        "⚠️  API: Rate limit exceeded (1000 req/hour)",
        foreground="black",
        background="yellow"
    )

    # === 9. GRADIENT EFFECT (Multiple messages) ===
    log.info("=" * 60)
    log.info("9. GRADIENT EFFECT")
    log.info("=" * 60)

    gradient_colors = ["light_red", "light_yellow", "light_green", "light_cyan", "light_blue", "light_magenta"]
    for i, color in enumerate(gradient_colors, 1):
        log.colored(f"  Gradient step {i}: {color} text", foreground=color)

    # === 10. DATA TYPE HIGHLIGHTING ===
    log.info("=" * 60)
    log.info("10. DATA TYPE HIGHLIGHTING")
    log.info("=" * 60)

    log.colored("Numbers: 42, 3.14, -123", foreground="cyan")
    log.colored("Boolean: True, False", foreground="magenta")
    log.colored("String: 'Hello, World!'", foreground="white")
    log.colored("URL: https://example.com/api", foreground="blue")

    print(f"\nGenerated log file: {log_file}")
    print(f"View with: logxpy-view {log_file}")
    print(f"Or with ASCII: logxpy-view {log_file} --ascii")
    print(f"Or without colors: logxpy-view {log_file} --no-colors")

if __name__ == "__main__":
    main()
