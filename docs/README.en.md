# 𝑓OS Library Documentation

[English](README.en.md) | [简体中文](../README.md)

𝑓OS is a lightweight command-line tool library designed for **MicroPython**, providing Linux-like file operations, system information viewing, WiFi management, and a **built-in miniature editor**.  
All commands are provided as functions and automatically output a blank line after execution for improved readability. Chinese filenames are correctly aligned.

## Main Features

- **File & Path Operations**: `pwd`, `cd`, `ls`, `mkdir`, `rmdir`, `cp`, `mv`, `rm`, `cat`, `touch`
- **Built-in Editor**: `edit` – edit text files directly in the REPL
- **System Information**: `uname`, `free`, `df`, `date`
- **WiFi Management**: `iwlist_scan` (scan), `iwconfig` (status/connect), `create_ap` (create hotspot), `ifconfig` (network config), `ntp_sync` (NTP time sync)
- **BLE REPL**: `start_ble_repl` (start), `stop_ble_repl` (stop)

## Installation

1. Save the complete `fos` code as `fos.py` (copy it to your MicroPython device, e.g., under `/flash` or `/sd`).
2. Import the module in the REPL:

```python
from fos import *
```

Or use a prefixed approach:

```python
import fos
fos.pwd()
```

## Quick Start

### 1. Basic File Operations

```python
>>> pwd()
/flash

>>> ls()
boot.py    main.py    lib

>>> ls(long=True)
Type Name       Size(B)
------------------------
F    boot.py       1024
F    main.py        512
D    lib              0

>>> mkdir("backup")
Created directory backup

>>> cp("boot.py", "backup/boot.py")
Copied boot.py to backup/boot.py

>>> mv("backup/boot.py", "backup/boot_new.py")
Moved backup/boot.py to backup/boot_new.py

>>> rm("backup/boot_new.py")
Removed backup/boot_new.py

>>> cat("boot.py")
# File content will be printed ...

>>> touch("test.txt")
Touched: test.txt

>>> rm("test.txt")
Removed test.txt

>>> rmdir("backup")
Removed directory backup
```

### 2. System Information

```python
>>> uname()
esp32 ESP32 v1.23.0 2024-01-01 ESP32 module with ESP32

>>> free()
               total     used    free
--------------------------------------
Mem:           112640    56789    55851

>>> df()
Filesystem    Size   Used   Available   Use%   Mounted on
---------------------------------------------------------
rootfs        1.5M   0.8M       0.7M    53%           /

>>> date()
Fri May 12 10:30:45 UTC 2023
```

### 3. WiFi Management

#### Scan for nearby networks

```python
>>> iwlist_scan()
SSID               RSSI  MAC               Encryption
-----------------------------------------------------
MyHomeWiFi          -45   aa:bb:cc:dd:ee:ff  WPA2-PSK
OfficeWiFi          -68   11:22:33:44:55:66  WPA/WPA2-PSK
```

#### Check wireless interface status

```python
>>> iwconfig()
Interface: wlan0 (STA)
Active: Yes
Connected: No
```

#### Connect to WiFi (provide SSID and password)

```python
>>> iwconfig("MyHomeWiFi", "password123")
Connecting to MyHomeWiFi ...
...
Connected successfully.
IP address: 192.168.1.100

>>> iwconfig()
Interface: wlan0 (STA)
Active: Yes
Connected: Yes
SSID: MyHomeWiFi
Signal: -45 dBm
IP address: 192.168.1.100
Netmask: 255.255.255.0
Gateway: 192.168.1.1
DNS: 192.168.1.1
```

#### Show full network configuration (including AP interface)

```python
>>> ifconfig()
Interface       IP            Netmask       Gateway       DNS           SSID         Status
---------------------------------------------------------------------------------------
wlan0 (STA)     192.168.1.100 255.255.255.0 192.168.1.1   192.168.1.1   MyHomeWiFi   Connected
wlan1 (AP)      0.0.0.0       0.0.0.0       0.0.0.0       0.0.0.0                    Inactive
```

#### Create an access point

```python
>>> create_ap("MyHotspot", "87654321")
Access Point created successfully.
SSID: MyHotspot
Security: WPA2-PSK
IP address: 192.168.4.1
```

#### Synchronise time via NTP (requires WiFi connection)

```python
>>> ntp_sync()
Syncing time with pool.ntp.org ...
Time synchronized successfully.
Fri May 12 10:31:00 UTC 2023
```

### 4. Edit Files

𝑓OS includes a miniature full-screen text editor that lets you create or modify text files directly in the REPL.

```python
>>> edit("boot.py")
```

After execution, the REPL enters the editor interface, displaying a style like:

```
 boot.py   | Lines:4 | Pos:1,1 | Ctrl+S:Save Ctrl+Q:Quit
# File content is printed here ...
```

- **Cursor movement**: Arrow keys
- **Save file**: `Ctrl+S`
- **Exit editor**: `Ctrl+Q`
- **Line number display**: The top bar always shows the current file name, total lines, and cursor position (line, column)

For detailed operation instructions, keyboard shortcuts, and advanced configuration (syntax highlighting, search/replace), please refer to the [𝑓OS Text Editor User Guide](./fos/editor/README.md).

> **Note**: The editor is suitable for relatively small text files (recommended < 64KB). Larger files may load slowly due to memory limitations. For binary files, use the `cp` command.

### 5. BLE REPL

Transfer data over BLE to achieve a wireless REPL connection. After starting, connect to the device from a computer via a BLE serial port.

- **Start BLE REPL**: `start_ble_repl()`
- **Stop BLE REPL**: `stop_ble_repl()`

## Command Reference

### File/Path Commands

| Command                    | Parameters                       | Description                                                                             |
| -------------------------- | -------------------------------- | --------------------------------------------------------------------------------------- |
| `pwd()`                    | none                             | Show current working directory                                                          |
| `cd(path)`                 | path                             | Change working directory                                                                |
| `ls(path='.', long=False)` | directory path, long format flag | Short format: tab-separated, auto-wrapped lines; long format: table with type/name/size |
| `mkdir(path)`              | directory name                   | Create directory (parent must exist)                                                    |
| `rmdir(path)`              | directory name                   | Remove empty directory                                                                  |
| `cp(src, dst, dir=False)`  | source, destination, copy dir    | Copy file or recursively copy directory (dir=True)                                      |
| `mv(src, dst)`             | source, destination              | Move/rename file or directory (destination must not exist)                              |
| `rm(path)`                 | file path                        | Delete file (cannot delete directories)                                                 |
| `cat(path)`                | file path                        | Print text file content                                                                 |
| `touch(path)`              | file path                        | Create an empty file (if exists, only updates timestamp – implementation only creates)  |
| `edit(path)`               | file path                        | Edit file with built-in miniature editor                                                |

### System Information Commands

| Command   | Description                                                  |
| --------- | ------------------------------------------------------------ |
| `uname()` | Display system information (kernel, version, hardware, etc.) |
| `free()`  | Show memory usage (tabular)                                  |
| `df()`    | Show filesystem disk space usage (tabular)                   |
| `date()`  | Display current UTC time (similar to Linux date format)      |

### WiFi Commands

| Command                           | Parameters                  | Description                                                                       |
| --------------------------------- | --------------------------- | --------------------------------------------------------------------------------- |
| `iwlist_scan()`                   | none                        | Scan WiFi networks, output table (SSID, signal strength, MAC, encryption type)    |
| `iwconfig(ssid=None, key='')`     | optional ssid and key       | No args: show current wireless interface status; with args: connect to given WiFi |
| `create_ap(ssid, key='')`         | hotspot name, optional key  | Create WiFi hotspot (encryption enabled only if key length ≥ 8)                   |
| `ifconfig()`                      | none                        | Show detailed network configuration for both STA and AP interfaces                |
| `ntp_sync(server="pool.ntp.org")` | optional NTP server address | Synchronise system time via NTP (requires WiFi connection)                        |

## Important Notes

- **Chinese support**: Filenames and WiFi SSIDs support Chinese display and alignment (Chinese character width counts as 2).
- **Error checking**: Most commands check whether source/destination exist and parent directories exist, preventing accidental mistakes.
- **WiFi dependency**: WiFi-related commands only work on MicroPython firmware that includes the `network` module (e.g., ESP8266, ESP32, Pico W). On boards without WiFi, calling them will print an error message.
- **Time synchronisation**: `ntp_sync` requires the `ntptime` module (usually built into MicroPython) and an active internet connection.
- **Editor memory**: The `edit` command reads the entire file into memory; very large files may fail. Recommend editing text files smaller than 64KB.
- **Memory footprint**: The library contains many functions, but they are only loaded at import time, making it suitable for resource-constrained embedded devices.

## Frequently Asked Questions

**Q: Why does `cp(dir=True)` require the destination parent directory to exist?**  
A: For safety, to avoid accidentally creating deep directories due to path errors. You can `mkdir` the destination parent first.

**Q: In `ls` long format, is the size unit bytes?**  
A: Yes, it shows exact byte counts for easy scripting. `df` automatically converts to K/M/G.

**Q: How can I display local time instead of UTC?**  
A: `date()` shows UTC by default. To display, for example, Beijing time (UTC+8), you can modify the `date()` function by adding 8 to the hour of the time tuple and handling day rollover.

**Q: Why is `cp` slow when copying large files?**  
A: Because MicroPython reads/writes files in chunks (e.g., 1KB). You can increase chunk size by modifying `chunk = fsrc.read(4096)` to improve speed.

**Q: How to copy/paste in the editor?**  
A: The current version supports clipboard emulation (`Ctrl+C` to copy selected text, `Ctrl+V` to paste), but due to terminal limitations, please refer to the detailed documentation.
