import gc
import os
import time

from .editor import edit

# 尝试导入 network 模块，若失败则标记 WiFi 不可用
try:
    import network

    _wifi_available = True
except ImportError:
    _wifi_available = False


# ========== 字符串显示宽度辅助函数 ==========
def _disp_len(s):
    """返回字符串的显示宽度（ASCII 1, 中文等宽字符 2）"""
    w = 0
    for ch in s:
        if ord(ch) > 0x7F:
            w += 2
        else:
            w += 1
    return w


def _pad(s, width, align="<"):
    cur = _disp_len(s)
    if cur >= width:
        return s
    spaces = " " * (width - cur)
    if align == "<":
        return s + spaces
    else:
        return spaces + s


# ========== 辅助检查函数 ==========
def _exists(path):
    try:
        os.stat(path)
        return True
    except:
        return False


def _is_dir(path):
    try:
        st = os.stat(path)
        return (st[0] & 0x4000) != 0
    except:
        return False


def _is_file(path):
    try:
        st = os.stat(path)
        return (st[0] & 0x4000) == 0
    except:
        return False


def _parent_exists(path):
    if "/" not in path:
        return True
    parent = path[: path.rfind("/")]
    if not parent:
        return True
    return _exists(parent)


# ========== 路径与目录操作 ==========
def pwd():
    print(os.getcwd())
    print()


def cd(path):
    try:
        os.chdir(path)
    except Exception as e:
        print("Error:", e)
    print()


def ls(path=".", long=False):
    try:
        items = os.listdir(path)
        if not long:
            sep = "    "
            sep_width = 4
            max_width = 80
            cur_line = []
            cur_width = 0
            for name in items:
                name_width = _disp_len(name)
                if cur_width == 0:
                    cur_line.append(name)
                    cur_width = name_width
                else:
                    if cur_width + sep_width + name_width <= max_width:
                        cur_line.append(name)
                        cur_width += sep_width + name_width
                    else:
                        print(sep.join(cur_line))
                        cur_line = [name]
                        cur_width = name_width
            if cur_line:
                print(sep.join(cur_line))
            print()
            return

        base = path.rstrip("/") + "/"
        entries = []
        max_name_width = 0
        max_size_len = 0
        for name in items:
            full = base + name
            try:
                st = os.stat(full)
                mode = st[0]
                is_dir = (mode & 0x4000) != 0
                size = st[6]
                typ = "D" if is_dir else "F"
            except:
                typ = "?"
                size = 0
            entries.append((name, typ, size))
            max_name_width = max(max_name_width, _disp_len(name))
            max_size_len = max(max_size_len, len(str(size)))

        header = (
            _pad("Type", 4, "<")
            + "  "
            + _pad("Name", max_name_width, "<")
            + "  "
            + _pad("Size(B)", max_size_len, ">")
        )
        print(header)
        print("-" * _disp_len(header))
        for name, typ, size in entries:
            line = (
                _pad(typ, 4, "<")
                + "  "
                + _pad(name, max_name_width, "<")
                + "  "
                + _pad(str(size), max_size_len, ">")
            )
            print(line)
        print()
    except Exception as e:
        print("Error:", e)
        print()


def mkdir(path):
    """创建目录，父目录必须存在"""
    if not _parent_exists(path):
        print("Error: Parent directory does not exist.")
        print()
        return
    try:
        os.mkdir(path)
        print("Created directory", path)
    except Exception as e:
        print("Error:", e)
    print()


def rmdir(path):
    """删除空目录"""
    if not _exists(path):
        print("Error: Directory does not exist.")
        print()
        return
    if not _is_dir(path):
        print("Error: Not a directory.")
        print()
        return
    try:
        os.rmdir(path)
        print("Removed directory", path)
    except Exception as e:
        print("Error:", e)
    print()


# ========== 文件操作 ==========
def cp(src, dst, dir=False):
    """
    复制文件或目录
    src: 源路径
    dst: 目标路径
    dir: 若为 True，则递归复制目录（源必须是目录）
    """
    try:
        if dir:
            # 复制目录
            if not _exists(src):
                print("Error: Source does not exist.")
                return
            if not _is_dir(src):
                print("Error: Source is not a directory.")
                return
            if "/" in dst and not _parent_exists(dst):
                print("Error: Parent directory of destination does not exist.")
                return
            if _exists(dst) and not _is_dir(dst):
                print("Error: Destination exists and is not a directory.")
                return

            def _copy_dir_recursive(s, d):
                try:
                    os.mkdir(d)
                except OSError:
                    pass
                for item in os.listdir(s):
                    sp = s + "/" + item
                    dp = d + "/" + item
                    try:
                        st = os.stat(sp)
                        if (st[0] & 0x4000) != 0:
                            _copy_dir_recursive(sp, dp)
                        else:
                            with open(sp, "rb") as fsrc:
                                with open(dp, "wb") as fdst:
                                    while True:
                                        chunk = fsrc.read(1024)
                                        if not chunk:
                                            break
                                        fdst.write(chunk)
                    except Exception as e:
                        print("Error copying", sp, ":", e)

            dst_effective = dst
            if _exists(dst) and _is_dir(dst):
                base_name = src.rstrip("/").split("/")[-1]
                dst_effective = dst.rstrip("/") + "/" + base_name
            _copy_dir_recursive(src.rstrip("/"), dst_effective)
            print("Copied directory", src, "to", dst_effective)
        else:
            # 文件复制
            if not _exists(src):
                print("Error: Source file does not exist.")
                return
            if not _is_file(src):
                print("Error: Source is not a regular file.")
                return
            if not _parent_exists(dst):
                print("Error: Parent directory of destination does not exist.")
                return
            if _exists(dst):
                print(
                    "Error: Destination already exists. Use mv or rm first if you want to replace."
                )
                return
            with open(src, "rb") as fsrc:
                with open(dst, "wb") as fdst:
                    while True:
                        chunk = fsrc.read(1024)
                        if not chunk:
                            break
                        fdst.write(chunk)
            print("Copied", src, "to", dst)
    except Exception as e:
        print("Error:", e)
    print()


def mv(src, dst):
    """移动或重命名文件/目录。目标不能已存在，父目录必须存在。"""
    if not _exists(src):
        print("Error: Source does not exist.")
        print()
        return
    if not _parent_exists(dst):
        print("Error: Parent directory of destination does not exist.")
        print()
        return
    if _exists(dst):
        print("Error: Destination already exists. Remove it first if needed.")
        print()
        return
    try:
        os.rename(src, dst)
        print("Moved", src, "to", dst)
    except Exception as e:
        print("Error:", e)
    print()


def rm(path):
    """删除文件（不能删除目录）"""
    if not _exists(path):
        print("Error: File does not exist.")
        print()
        return
    if not _is_file(path):
        print("Error: Path is a directory. Use rmdir for directories.")
        print()
        return
    try:
        os.remove(path)
        print("Removed", path)
    except Exception as e:
        print("Error:", e)
    print()


def cat(path):
    """显示文本文件内容"""
    if not _exists(path):
        print("Error: File does not exist.")
        print()
        return
    if not _is_file(path):
        print("Error: Path is a directory.")
        print()
        return
    try:
        with open(path, "r") as f:
            print(f.read(), end="")
    except Exception as e:
        print("Error:", e)
    print()


def touch(path):
    """创建空文件（若不存在）"""
    try:
        with open(path, "a"):
            pass
        print("Touched:", path)
    except Exception as e:
        print("Error:", e)
    print()


# ========== 系统信息（不依赖WiFi） ==========
def uname():
    """显示系统信息（类似于 Linux uname -a）"""
    try:
        u = os.uname()
        print(u.sysname, u.nodename, u.release, u.version, u.machine)
    except Exception as e:
        print("Error:", e)
    print()


def free():
    """显示内存使用情况（表格形式）"""
    try:
        total = gc.mem_alloc() + gc.mem_free()
        used = gc.mem_alloc()
        free_mem = gc.mem_free()
        label = "Mem:"
        values = [total, used, free_mem]
        headers = ["", "total", "used", "free"]
        col_widths = [0, 0, 0, 0]
        col_widths[0] = _disp_len(label)
        for i, v in enumerate(values):
            s = str(v)
            w = max(_disp_len(headers[i + 1]), len(s))
            col_widths[i + 1] = w
        header_line = (
            _pad(headers[0], col_widths[0], "<")
            + "  "
            + _pad(headers[1], col_widths[1], ">")
            + "  "
            + _pad(headers[2], col_widths[2], ">")
            + "  "
            + _pad(headers[3], col_widths[3], ">")
        )
        print(header_line)
        print("-" * _disp_len(header_line))
        data_line = (
            _pad(label, col_widths[0], "<")
            + "  "
            + _pad(str(values[0]), col_widths[1], ">")
            + "  "
            + _pad(str(values[1]), col_widths[2], ">")
            + "  "
            + _pad(str(values[2]), col_widths[3], ">")
        )
        print(data_line)
    except Exception as e:
        print("Error:", e)
    print()


def df():
    """显示文件系统磁盘空间使用情况（表格形式）"""
    try:
        if not hasattr(os, "statvfs"):
            print("Error: statvfs not supported on this platform.")
            print()
            return
        vfs = os.statvfs("/")
        block_size = vfs[0]
        total_blocks = vfs[2]
        free_blocks = vfs[3]
        total = block_size * total_blocks
        free = block_size * free_blocks
        used = total - free
        usage = (used * 100) // total if total > 0 else 0

        def _fmt_size(sz):
            if sz >= 1024 * 1024 * 1024:
                return "%.1fG" % (sz / (1024 * 1024 * 1024))
            elif sz >= 1024 * 1024:
                return "%.1fM" % (sz / (1024 * 1024))
            elif sz >= 1024:
                return "%.1fK" % (sz / 1024)
            else:
                return "%dB" % sz

        filesystem = "rootfs"
        mount = "/"
        headers = ["Filesystem", "Size", "Used", "Available", "Use%", "Mounted on"]
        row = [
            filesystem,
            _fmt_size(total),
            _fmt_size(used),
            _fmt_size(free),
            "%d%%" % usage,
            mount,
        ]
        col_widths = []
        for i in range(len(headers)):
            w = max(_disp_len(headers[i]), _disp_len(row[i]))
            col_widths.append(w)
        header_parts = []
        for i, h in enumerate(headers):
            align = "<" if i == 0 or i == 5 else ">"
            header_parts.append(_pad(h, col_widths[i], align))
        header_line = "  ".join(header_parts)
        print(header_line)
        print("-" * _disp_len(header_line))
        row_parts = []
        for i, val in enumerate(row):
            align = "<" if i == 0 or i == 5 else ">"
            row_parts.append(_pad(val, col_widths[i], align))
        data_line = "  ".join(row_parts)
        print(data_line)
    except Exception as e:
        print("Error:", e)
    print()


def date():
    """显示当前时间（格式：Weekday Month Day HH:MM:SS UTC Year）"""
    try:
        tm = time.localtime()
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        wday = weekdays[tm[6] % 7]
        time_str = "%s %s %02d %02d:%02d:%02d UTC %d" % (
            wday,
            months[tm[1] - 1],
            tm[2],
            tm[3],
            tm[4],
            tm[5],
            tm[0],
        )
        print(time_str)
    except Exception as e:
        print("Error:", e)
    print()


# ========== WiFi 功能（扫描、连接、创建热点、NTP同步、ifconfig） ==========
if _wifi_available:

    def iwlist_scan():
        """扫描 WiFi 网络，输出表格（SSID, RSSI, MAC, 加密）"""
        try:
            wlan = network.WLAN(network.STA_IF)
            if not wlan.active():
                wlan.active(True)
            results = wlan.scan()
            if not results:
                print("No WiFi networks found.")
                print()
                return

            auth_modes = {
                0: "OPEN",
                1: "WEP",
                2: "WPA-PSK",
                3: "WPA2-PSK",
                4: "WPA/WPA2-PSK",
            }
            entries = []
            max_ssid_w = _disp_len("SSID")
            max_rssi_w = _disp_len("RSSI")
            max_mac_w = _disp_len("MAC")
            max_auth_w = _disp_len("Encryption")

            for net in results:
                ssid_raw = net[0]
                ssid = (
                    ssid_raw.decode() if isinstance(ssid_raw, bytes) else str(ssid_raw)
                )
                if not ssid:
                    ssid = "<hidden>"
                rssi = str(net[3])
                bssid = ":".join(f"{b:02x}" for b in net[1])
                auth = auth_modes.get(net[4], f"UNKNOWN({net[4]})")
                entries.append((ssid, rssi, bssid, auth))
                max_ssid_w = max(max_ssid_w, _disp_len(ssid))
                max_rssi_w = max(max_rssi_w, _disp_len(rssi))
                max_mac_w = max(max_mac_w, _disp_len(bssid))
                max_auth_w = max(max_auth_w, _disp_len(auth))

            header = (
                _pad("SSID", max_ssid_w, "<")
                + "  "
                + _pad("RSSI", max_rssi_w, ">")
                + "  "
                + _pad("MAC", max_mac_w, "<")
                + "  "
                + _pad("Encryption", max_auth_w, "<")
            )
            print(header)
            print("-" * _disp_len(header))
            for ssid, rssi, mac, auth in entries:
                line = (
                    _pad(ssid, max_ssid_w, "<")
                    + "  "
                    + _pad(rssi, max_rssi_w, ">")
                    + "  "
                    + _pad(mac, max_mac_w, "<")
                    + "  "
                    + _pad(auth, max_auth_w, "<")
                )
                print(line)
            print()
        except Exception as e:
            print("Error: WiFi scan failed -", e)
            print()

    def iwconfig(ssid=None, key=""):
        """
        WiFi 配置命令：
        - 无参数：显示当前无线接口状态（类似 Linux iwconfig）
        - 带参数：连接指定的 WiFi 网络（ssid, key）
        """
        try:
            wlan = network.WLAN(network.STA_IF)
            if ssid is not None:
                # 连接模式
                if not wlan.active():
                    wlan.active(True)
                if wlan.isconnected() and wlan.config("ssid") == ssid:
                    print("Already connected to", ssid)
                    ip = wlan.ifconfig()[0]
                    print("IP address:", ip)
                    print()
                    return
                if wlan.isconnected():
                    wlan.disconnect()
                    time.sleep(0.5)
                print("Connecting to", ssid, "...")
                wlan.connect(ssid, key)
                timeout = 15
                start = time.time()
                while not wlan.isconnected() and (time.time() - start) < timeout:
                    time.sleep(0.5)
                    print(".", end="")
                print()
                if wlan.isconnected():
                    ip = wlan.ifconfig()[0]
                    print("Connected successfully.")
                    print("IP address:", ip)
                else:
                    print("Connection failed. Please check SSID and password.")
                print()
            else:
                # 显示状态模式
                active = wlan.active()
                if not active:
                    print("Wi-Fi interface is inactive.")
                    print()
                    return
                connected = wlan.isconnected()
                if connected:
                    ssid_cur = wlan.config("ssid")
                    ip, netmask, gw, dns = wlan.ifconfig()
                    rssi = ""
                    try:
                        rssi = wlan.status("rssi")
                    except:
                        pass
                    print("Interface: wlan0 (STA)")
                    print("Active: Yes")
                    print("Connected: Yes")
                    print("SSID: %s" % ssid_cur)
                    if rssi:
                        print("Signal: %d dBm" % rssi)
                    print("IP address: %s" % ip)
                    print("Netmask: %s" % netmask)
                    print("Gateway: %s" % gw)
                    print("DNS: %s" % dns)
                else:
                    print("Interface: wlan0 (STA)")
                    print("Active: Yes")
                    print("Connected: No")
                print()
        except Exception as e:
            print("Error:", e)
            print()

    def create_ap(ssid, key=""):
        """创建 WiFi 热点"""
        try:
            ap = network.WLAN(network.AP_IF)
            ap.active(False)
            time.sleep(0.2)
            ap.active(True)
            if key:
                if len(key) < 8:
                    print(
                        "Warning: Password must be at least 8 characters. Using open network instead."
                    )
                    ap.config(ssid=ssid, authmode=network.AUTH_OPEN)
                else:
                    ap.config(
                        ssid=ssid, authmode=network.AUTH_WPA_WPA2_PSK, password=key
                    )
            else:
                ap.config(ssid=ssid, authmode=network.AUTH_OPEN)
            ip = ap.ifconfig()[0]
            print("Access Point created successfully.")
            print("SSID:", ssid)
            print("Security:", "WPA2-PSK" if key and len(key) >= 8 else "Open")
            print("IP address:", ip)
        except Exception as e:
            print("Error: Failed to create access point -", e)
        print()

    def ntp_sync(server="pool.ntp.org"):
        """
        通过 NTP 同步系统时间（需要 WiFi 连接）
        server: NTP 服务器地址
        """
        try:
            wlan = network.WLAN(network.STA_IF)
            if not wlan.isconnected():
                print("Error: WiFi not connected. Use iwconfig() first.")
                print()
                return
        except Exception as e:
            print("Error: Failed to check WiFi status -", e)
            print()
            return

        try:
            import ntptime

            ntptime.host = server
            print("Syncing time with", server, "...")
            ntptime.settime()
            print("Time synchronized successfully.")
            date()
        except ImportError:
            print("Error: ntptime module not available on this firmware.")
            print()
        except Exception as e:
            print("Error: NTP sync failed -", e)
            print()

    def ifconfig():
        """显示网络接口配置（STA 和 AP），类似 Linux ifconfig"""
        try:
            sta = network.WLAN(network.STA_IF)
            ap = network.WLAN(network.AP_IF)
            # 获取 STA 信息
            sta_active = sta.active()
            if sta_active:
                sta_ifconfig = sta.ifconfig()
                sta_connected = sta.isconnected()
                sta_ssid = sta.config("ssid") if sta_connected else ""
                sta_status = "Connected" if sta_connected else "Disconnected"
            else:
                sta_ifconfig = ("0.0.0.0", "0.0.0.0", "0.0.0.0", "0.0.0.0")
                sta_ssid = ""
                sta_status = "Inactive"
            # 获取 AP 信息
            ap_active = ap.active()
            if ap_active:
                ap_ifconfig = ap.ifconfig()
                ap_ssid = ap.config("ssid")
                ap_status = "Active"
            else:
                ap_ifconfig = ("0.0.0.0", "0.0.0.0", "0.0.0.0", "0.0.0.0")
                ap_ssid = ""
                ap_status = "Inactive"
            # 构建表格数据
            headers = ["Interface", "IP", "Netmask", "Gateway", "DNS", "SSID", "Status"]
            rows = [
                [
                    "wlan0 (STA)",
                    sta_ifconfig[0],
                    sta_ifconfig[1],
                    sta_ifconfig[2],
                    sta_ifconfig[3],
                    sta_ssid,
                    sta_status,
                ],
                [
                    "wlan1 (AP)",
                    ap_ifconfig[0],
                    ap_ifconfig[1],
                    ap_ifconfig[2],
                    ap_ifconfig[3],
                    ap_ssid,
                    ap_status,
                ],
            ]
            col_widths = [_disp_len(h) for h in headers]
            for row in rows:
                for i, val in enumerate(row):
                    w = _disp_len(val)
                    if w > col_widths[i]:
                        col_widths[i] = w
            header_parts = [
                _pad(headers[i], col_widths[i], "<") for i in range(len(headers))
            ]
            header_line = "  ".join(header_parts)
            print(header_line)
            print("-" * _disp_len(header_line))
            for row in rows:
                row_parts = [_pad(row[i], col_widths[i], "<") for i in range(len(row))]
                data_line = "  ".join(row_parts)
                print(data_line)
            print()
        except Exception as e:
            print("Error:", e)
            print()

else:
    # 无 WiFi 支持时的占位函数
    def iwlist_scan():
        print("Error: WiFi not supported on this board (network module missing).")
        print()

    def iwconfig(ssid=None, key=""):
        print("Error: WiFi not supported on this board (network module missing).")
        print()

    def create_ap(ssid, key=""):
        print("Error: WiFi not supported on this board (network module missing).")
        print()

    def ntp_sync(server="pool.ntp.org"):
        print("Error: WiFi not supported, cannot sync time.")
        print()

    def ifconfig():
        print("Error: WiFi not supported on this board (network module missing).")
        print()
