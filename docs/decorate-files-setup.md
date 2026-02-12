# VSCode: decorate-files-and-folders Setup

Extension: `arturodent.decorate-files-and-folders` v0.1.5

## What You Actually Need

Three layers of settings must ALL be present:

### 1. VS Code Built-in (enable decoration rendering)

```json
"explorer.decorations.colors": true,
"explorer.decorations.badges": true,
"workbench.editor.decorations.colors": true,
"workbench.editor.decorations.badges": true
```

### 2. Extension Toggle (enable file path matching)

```json
"decorateFiles.decorations.apply": {
    "enableFilePaths": true
}
```

All toggles default to `false` - you MUST enable `enableFilePaths`.

### 3. Color Definitions (two parts)

**Part A** - `decorateFiles.filePaths`: maps file patterns to colors.

```json
"decorateFiles.filePaths": {
    "CLAUDE.md": "#ff0000",
    "uv.lock": "#15151518"
}
```

**Part B** - `workbench.colorCustomizations`: defines the actual ThemeColor values.

```json
"workbench.colorCustomizations": {
    "decorateFiles.path.CLAUDE.md": "#ff0000",
    "decorateFiles.path.uv.lock": "#15151518"
}
```

Both parts are required. Keep colors in sync between them.
- `filePaths` — tells the extension **which files to match** (default color)
- `colorCustomizations` — **overrides** the actual rendered color (wins if set)

JSON has no variables, so document your color values in comments:
```jsonc
// dim:  #82808060  (gray, 37% opacity)
// red:  #ff0000    (bright red)
```

## Pattern Formats

| Pattern | Matches | ThemeColor ID |
|---------|---------|---------------|
| `CLAUDE.md` | Any path containing "CLAUDE.md" | `decorateFiles.path.CLAUDE.md` |
| `.yaml` | All `.yaml` files | `decorateFiles.extension.yaml` |
| `docs/` | Folder name only | `decorateFiles.folderName.docs` |
| `docs/**` | Folder + all descendants | `decorateFiles.folderAndFiles.docs` |
| `src/foo.ts` | Exact path | `decorateFiles.path.src___foo.ts` |

## ThemeColor ID Encoding

| Character | Replaced with |
|-----------|---------------|
| `-` (hyphen) | `__` (2 underscores) |
| `/` (slash) | `___` (3 underscores) |

## Color Format

- `#RGB` - 3 hex digits
- `#RGBA` - 4 hex digits (with opacity)
- `#RRGGBB` - 6 hex digits
- `#RRGGBBAA` - 8 hex digits (with opacity, `00`=transparent, `ff`=opaque)

## Gotchas

- Changes require **window reload** (`Ctrl+Shift+P` -> "Reload Window")
- First match wins (top-to-bottom priority)
- Only forward slashes `/` for paths
- VS Code problem decorations override this extension
