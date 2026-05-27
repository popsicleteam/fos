# 𝑓OS 库介绍

[English](docs/README.en.md)

𝑓OS 是一个为 **MicroPython** 设计的轻量级命令行工具库，提供了类似 Linux 的文件操作、系统信息查看、WiFi 管理以及**内置微型编辑器**功能。  
所有命令均以函数形式提供，执行后会自动输出一个空行以提升可读性，支持中文文件名的正确对齐显示。

## 主要功能

- **文件与路径操作**：`pwd`, `cd`, `ls`, `mkdir`, `rmdir`, `cp`, `mv`, `rm`, `cat`, `touch`
- **内置编辑器**：`edit` – 在 REPL 中直接编辑文本文件
- **系统信息**：`uname`, `free`, `df`, `date`
- **WiFi 管理**：`iwlist_scan`(扫描), `iwconfig`(状态查看/连接), `create_ap`(创建热点), `ifconfig`(网络配置), `ntp_sync`(NTP 时间同步)
- **BLE REPL**：`start_ble_repl`(开启), `stop_ble_repl`(停止)

## 安装方法

1. 将完整的 `fos` 代码保存为 `fos.py` 文件（复制到 MicroPython 设备上，如 `/flash` 或 `/sd` 路径下）。
2. 在 REPL 中导入模块：

```python
from fos import *
```

或者使用带前缀的方式：

```python
import fos
fos.pwd()
```

## 快速上手

### 1. 基本文件操作

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
# 文件内容会打印出来 ...

>>> touch("test.txt")
Touched: test.txt

>>> rm("test.txt")
Removed test.txt

>>> rmdir("backup")
Removed directory backup
```

### 2. 系统信息查看

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

### 3. WiFi 管理

#### 扫描周围网络

```python
>>> iwlist_scan()
SSID               RSSI  MAC               Encryption
-----------------------------------------------------
MyHomeWiFi          -45   aa:bb:cc:dd:ee:ff  WPA2-PSK
OfficeWiFi          -68   11:22:33:44:55:66  WPA/WPA2-PSK
```

#### 查看无线网卡状态

```python
>>> iwconfig()
Interface: wlan0 (STA)
Active: Yes
Connected: No
```

#### 连接 WiFi（提供 ssid 和 密码）

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

#### 查看完整网络配置（包括热点接口）

```python
>>> ifconfig()
Interface       IP            Netmask       Gateway       DNS           SSID         Status
---------------------------------------------------------------------------------------
wlan0 (STA)     192.168.1.100 255.255.255.0 192.168.1.1   192.168.1.1   MyHomeWiFi   Connected
wlan1 (AP)      0.0.0.0       0.0.0.0       0.0.0.0       0.0.0.0                    Inactive
```

#### 创建热点

```python
>>> create_ap("MyHotspot", "87654321")
Access Point created successfully.
SSID: MyHotspot
Security: WPA2-PSK
IP address: 192.168.4.1
```

#### 同步时间（NTP，需要已连接 WiFi）

```python
>>> ntp_sync()
Syncing time with pool.ntp.org ...
Time synchronized successfully.
Fri May 12 10:31:00 UTC 2023
```

### 4. 编辑文件

𝑓OS 内置了一个微型全屏文本编辑器，可以在 REPL 中直接创建或修改文本文件。

```python
>>> edit("boot.py")
```

执行后，REPL 会进入编辑器界面，显示如下风格：

```
 boot.py   | Lines:4 | Pos:1,1 | Ctrl+S:Save Ctrl+Q:Quit
# 文件内容会打印出来 ...
```

- **光标移动**：方向键
- **保存文件**：`Ctrl+S`
- **退出编辑器**：`Ctrl+Q`
- **行号显示**：顶部始终显示当前文件名、总行数、行列位置

详细的操作说明、快捷键列表以及高级配置（语法高亮、搜索替换等）请参阅 [𝑓OS 文本编辑器使用说明](./fos/editor/README.zh-Hans.md)。

> **注意**：编辑器适用于较小的文本文件（建议 < 64KB），大文件可能会因内存限制而加载缓慢。对于二进制文件请使用 `cp` 命令。

### 5. BLE REPL

通过 BLE 传输数据，实现无线 REPL 连接。启动后，电脑端通过 BLE 串口连接到设备。

- **启动 BLE REPL**：`start_ble_repl()`
- **停止 BLE REPL**：`stop_ble_repl()`

## 命令参考

### 文件/路径命令

| 命令                       | 参数                   | 说明                                                        |
| -------------------------- | ---------------------- | ----------------------------------------------------------- |
| `pwd()`                    | 无                     | 显示当前工作目录                                            |
| `cd(path)`                 | 路径                   | 切换工作目录                                                |
| `ls(path='.', long=False)` | 目录路径, 是否长格式   | 短格式：Tab分隔、自动换行；长格式：表格显示类型、名称、大小 |
| `mkdir(path)`              | 目录名                 | 创建目录（父目录必须存在）                                  |
| `rmdir(path)`              | 目录名                 | 删除空目录                                                  |
| `cp(src, dst, dir=False)`  | 源, 目标, 是否复制目录 | 复制文件或递归复制目录（dir=True）                          |
| `mv(src, dst)`             | 源, 目标               | 移动/重命名文件或目录（目标不能已存在）                     |
| `rm(path)`                 | 文件路径               | 删除文件（不能删目录）                                      |
| `cat(path)`                | 文件路径               | 打印文本文件内容                                            |
| `touch(path)`              | 文件路径               | 创建空文件（存在则仅更新时间戳，但因实现限制仅创建）        |
| `edit(path)`               | 文件路径               | 使用内置微型编辑器编辑文件                                  |

### 系统信息命令

| 命令      | 说明                                     |
| --------- | ---------------------------------------- |
| `uname()` | 显示系统信息（内核、版本、硬件等）       |
| `free()`  | 显示内存使用情况（表格化）               |
| `df()`    | 显示文件系统磁盘空间使用情况（表格化）   |
| `date()`  | 显示当前 UTC 时间（格式类似 Linux date） |

### WiFi 命令

| 命令                              | 参数                   | 说明                                                      |
| --------------------------------- | ---------------------- | --------------------------------------------------------- |
| `iwlist_scan()`                   | 无                     | 扫描 WiFi 网络，输出表格（SSID、信号强度、MAC、加密类型） |
| `iwconfig(ssid=None, key='')`     | 可选 ssid 和 key       | 无参：显示当前无线接口状态；有参：连接指定 WiFi           |
| `create_ap(ssid, key='')`         | 热点名, 密码（可选）   | 创建 WiFi 热点（密码长度≥8位才启用加密）                  |
| `ifconfig()`                      | 无                     | 显示 STA 和 AP 接口的详细网络配置                         |
| `ntp_sync(server="pool.ntp.org")` | NTP 服务器地址（可选） | 通过 NTP 同步系统时间（需要已连接 WiFi）                  |

## 注意事项

- **中文支持**：文件名、WiFi SSID 均支持中文显示与对齐（中文字符宽度按 2 计算）。
- **错误检查**：大多数命令会检查源/目标是否存在、父目录是否存在等，避免误操作。
- **WiFi 依赖**：WiFi 相关命令仅在支持 `network` 模块的 MicroPython 固件（如 ESP8266、ESP32、Pico W）上有效；无 WiFi 的板子调用时会打印错误信息。
- **时间同步**：`ntp_sync` 需要 `ntptime` 模块（MicroPython 通常内置），且必须已连接因特网。
- **编辑器内存**：`edit` 命令会将整个文件读入内存，对于超大文件可能失败。建议编辑小于 64KB 的文本文件。
- **内存占用**：该库使用了大量函数，但仅会在导入时加载，适合资源有限的嵌入式设备。

## 常见问题

**Q: 为什么 `cp(dir=True)` 复制目录时目标父目录必须存在？**  
A: 为了安全，避免因路径错误导致意外创建深层目录。你可以先 `mkdir` 目标父目录。

**Q: `ls` 长格式中的大小单位是字节？**  
A: 是的，显示精确字节数，便于脚本处理。`df` 中则自动转为 K/M/G。

**Q: 如何让时间显示本地时区而不是 UTC？**  
A: `date()` 默认显示 UTC。如需显示北京时间（UTC+8），可自行修改 `date()` 函数，在时间元组的小时上加 8 并处理跨日。

**Q: 为什么 `cp` 复制大文件时很慢？**  
A: 因为 MicroPython 的文件读写是逐块（1KB）进行的，你可以修改 `chunk = fsrc.read(4096)` 提升速度。

**Q: 编辑器中如何复制/粘贴？**  
A: 当前版本支持剪贴板模拟（使用 `Ctrl+C` 复制选中文本，`Ctrl+V` 粘贴），但受限于终端环境，建议参考详细文档。
