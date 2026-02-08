#!/usr/bin/env python3
"""Capture logxpy-view output as HTML and PNG screenshot."""

import re
import subprocess
import sys
from pathlib import Path


def generate_log():
    """Generate log file if needed."""
    log_file = Path("xxx_3level_nested_colored.log")
    if not log_file.exists():
        print("Generating log file...")
        subprocess.run(["python", "xxx_3level_nested_colored.py"], check=True)


def capture_output(mode: str = "oneline") -> str:
    """Capture logxpy-view output."""
    cmd = ["logxpy-cli-view", "render", "xxx_3level_nested_colored.log"]
    if mode == "tree":
        cmd.extend(["--format", "tree"])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + result.stderr


def ansi_to_html(text: str) -> str:
    """Convert ANSI escape codes to HTML with proper styling."""
    # Escape HTML special chars
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Remove the return symbol
    text = text.replace('⏎', '')
    
    # Color mapping for 256 colors (foreground)
    color_map = {
        '38;5;0': '#000000', '38;5;1': '#ff5555', '38;5;2': '#50fa7b',
        '38;5;3': '#f1fa8c', '38;5;4': '#8be9fd', '38;5;5': '#ff79c6',
        '38;5;6': '#8be9fd', '38;5;7': '#ffffff', '38;5;8': '#6c7086',
        '38;5;15': '#ffffff',
    }
    
    # Background color mapping
    bg_color_map = {
        '48;5;0': '#000000', '48;5;1': '#ff5555', '48;5;2': '#50fa7b',
        '48;5;3': '#f1fa8c', '48;5;4': '#8be9fd', '48;5;5': '#ff79c6',
        '48;5;6': '#8be9fd', '48;5;7': '#ffffff', '48;5;8': '#6c7086',
        '48;5;15': '#ffffff',
    }
    
    result = []
    open_tags = 0
    i = 0
    
    while i < len(text):
        if text[i:i+2] == '\x1b[':
            # Found ANSI escape
            end = text.find('m', i)
            if end != -1:
                codes = text[i+2:end]
                
                if codes == '0':
                    # Reset - close all open spans
                    while open_tags > 0:
                        result.append('</span>')
                        open_tags -= 1
                elif codes == '1':
                    # Bold
                    result.append('<span style="font-weight:bold">')
                    open_tags += 1
                elif codes == '2':
                    # Dim
                    result.append('<span style="opacity:0.7">')
                    open_tags += 1
                elif codes in color_map:
                    # Foreground color
                    if open_tags > 0:
                        result.append('</span>')
                        open_tags -= 1
                    result.append(f'<span style="color:{color_map[codes]}">')
                    open_tags += 1
                elif codes in bg_color_map:
                    # Background color
                    if open_tags > 0:
                        result.append('</span>')
                        open_tags -= 1
                    result.append(f'<span style="background-color:{bg_color_map[codes]}">')
                    open_tags += 1
                
                i = end + 1
                continue
        
        result.append(text[i])
        i += 1
    
    # Close any remaining spans
    while open_tags > 0:
        result.append('</span>')
        open_tags -= 1
    
    return ''.join(result)


def create_html(output: str, mode: str) -> Path:
    """Create HTML file with captured output."""
    html_file = Path(f"{mode}.html")
    html_output = ansi_to_html(output)
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>logxpy-view {mode}</title>
    <style>
        body {{
            background: #1e1e2e;
            margin: 0;
            padding: 20px;
            font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, monospace;
            font-size: 13px;
            line-height: 1.4;
        }}
        .container {{
            background: #11111b;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            display: inline-block;
        }}
        pre {{
            margin: 0;
            color: #cdd6f4;
            white-space: pre;
            font-family: inherit;
        }}
    </style>
</head>
<body>
    <div class="container">
        <pre>{html_output}</pre>
    </div>
</body>
</html>'''
    
    html_file.write_text(html_content, encoding='utf-8')
    print(f"HTML saved: {html_file}")
    return html_file


def take_screenshot(html_file: Path, mode: str) -> Path:
    """Take screenshot using playwright."""
    png_file = Path(f"{mode}.png")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f'file://{html_file.absolute()}')
            page.wait_for_load_state('networkidle')
            
            # Get content dimensions
            dimensions = page.evaluate("""() => {
                const pre = document.querySelector('pre');
                const rect = pre.getBoundingClientRect();
                return {
                    width: Math.ceil(rect.width) + 40,
                    height: Math.ceil(rect.height) + 40
                };
            }""")
            
            page.set_viewport_size({
                'width': max(dimensions['width'], 800),
                'height': max(dimensions['height'], 400)
            })
            
            page.screenshot(path=str(png_file))
            browser.close()
        
        print(f"Screenshot saved: {png_file}")
        return png_file
    except Exception as e:
        print(f"Screenshot failed: {e}")
        return None


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "oneline"
    if mode not in ("oneline", "tree", "t"):
        mode = "oneline"
    if mode == "t":
        mode = "tree"
    
    print(f"Capturing {mode} view...")
    generate_log()
    
    output = capture_output(mode)
    html_file = create_html(output, mode)
    png_file = take_screenshot(html_file, mode)
    
    print()
    if png_file and png_file.exists():
        print(f"✅ Screenshot: {png_file}")
    print(f"✅ HTML: {html_file}")


if __name__ == "__main__":
    main()
