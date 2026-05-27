# 𝑓OS Text Editor User Guide

[简体中文](editor.md)

A **plain text editor** written specifically for **MicroPython** (e.g., ESP32, RP2040, PyBoard, etc.). It provides basic editing capabilities for directly modifying files on the device through a serial terminal (PuTTY, minicom, screen, etc.).

## ✨ Features

- Supports editing ASCII text files and creating new files
- Arrow keys for cursor movement; Home/End for quick jump to line start/end
- Insert/delete characters, line break, Tab expands to 4 spaces
- `Ctrl+S` to save file, `Ctrl+Q` to exit editor
- Auto-scrolling, status bar showing file name, modified flag, cursor position
- Customizable terminal dimensions (width, height)
- Automatically clears the screen and restores original terminal state on exit

## 🚀 Usage

### Import and edit a file

```python
import fos
fos.edit("boot.py")          # default 80x24 terminal
# fos.edit("boot.py", width=100, height=30)   # custom dimensions
```

After execution, the REPL enters the editor interface, displaying a style similar to:

```
 boot.py   | Lines:4 | Pos:1,1 | Ctrl+S:Save Ctrl+Q:Quit
# File content is printed here...
```

## ⌨️ Keyboard Shortcuts & Operations

| Key                              | Function                                             |
| -------------------------------- | ---------------------------------------------------- |
| Arrow keys ↑ ↓ ← →               | Move cursor                                          |
| Home / End                       | Jump to beginning / end of line                      |
| Regular characters (incl. space) | Insert character                                     |
| Backspace                        | Delete character before cursor                       |
| Delete                           | (Not fully implemented – can delete and merge lines) |
| Enter                            | New line                                             |
| Tab                              | Insert 4 spaces                                      |
| **Ctrl+S**                       | **Save file**                                        |
| **Ctrl+Q**                       | **Exit editor**                                      |

## ⚠️ Important Notes

1. **Terminal flow control**  
   If the terminal becomes unresponsive after pressing `Ctrl+S` (XON/XOFF flow control), run the following command on the **host terminal** once:

   ```bash
   stty -ixon
   ```

   Then reconnect to your MicroPython device.

2. **Character set limitation**  
   Currently only ASCII characters (English letters, numbers, basic symbols) are supported. Unicode characters (e.g., Chinese, Japanese) are not supported.

3. **Terminal dimensions**  
   The editor defaults to 80 columns × 24 rows. **This must match the actual terminal window size**, otherwise cursor positioning will be incorrect. If using a different size, pass the actual column and row counts to `edit(filename, width=actual_cols, height=actual_rows)`.

## 🔧 Frequently Asked Questions

- **Q:** Why doesn't the status bar appear?  
  **A:** Usually because the terminal height does not match the `height` parameter. Check the actual number of rows in your terminal window (e.g., in PuTTY you can resize the window and look at the configuration), and pass the correct `height` when calling `edit()`.

- **Q:** When I press Backspace, the entire line is deleted?  
  **A:** When the cursor is at the beginning of a line, Backspace merges the current line with the end of the previous line – this is normal editor behavior.

- **Q:** Can I edit long lines exceeding 80 columns?  
  **A:** Yes. Long lines are visually truncated (the end is shown as `>`), but the cursor can move into the truncated part (keep pressing the right arrow key to move further right while editing).
