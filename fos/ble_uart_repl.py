import io
import os
import struct
import time

import bluetooth
import machine

from micropython import const

_UART_SERVICE_UUID = bluetooth.UUID("f0b4a3c2-1d2e-3f4a-5b6c-7d8e9f0a1b2c")
_UART_RX_CHAR_UUID = bluetooth.UUID("f0b4a3c2-1d2e-3f4a-5b6c-7d8e9f0a1b2d")
_UART_TX_CHAR_UUID = bluetooth.UUID("f0b4a3c2-1d2e-3f4a-5b6c-7d8e9f0a1b2e")

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)


class BLEUARTStream(io.IOBase):
    def __init__(self, ble, name=None):
        self._ble = ble
        self._conn_handle = None
        self._tx_handle = None
        self._rx_handle = None
        self._rx_buffer = bytearray()
        self._rx_buffer_size = 256
        self._connected = False
        self._active = True
        self._need_restart_adv = False
        self._ctrl_d_received = False
        self._name = name

        self._ble.active(True)
        self._ble.irq(self._irq)
        self._register_services()
        self._advertise()

    def _register_services(self):
        service = (
            _UART_SERVICE_UUID,
            (
                (_UART_TX_CHAR_UUID, _FLAG_READ | _FLAG_NOTIFY),
                (_UART_RX_CHAR_UUID, _FLAG_WRITE),
            ),
        )
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services(
            (service,)
        )
        self._ble.gatts_set_buffer(self._rx_handle, self._rx_buffer_size, True)

    def _get_device_name_bytes(self):
        if self._name is None:
            uid = machine.unique_id()
            uid_suffix = "{:02x}{:02x}".format(uid[-2], uid[-1])
            name_str = "ble-" + uid_suffix
        elif self._name == "":
            return None
        else:
            name_str = self._name

        name_bytes = name_str.encode("utf-8")
        if len(name_bytes) > 29:
            name_bytes = name_bytes[:29]
        return struct.pack("BB", len(name_bytes) + 1, 0x09) + name_bytes

    def _advertise(self):
        flags = b"\x02\x01\x06"
        uuid_bytes = bytes(_UART_SERVICE_UUID)
        service_adv = struct.pack("BB", len(uuid_bytes) + 1, 0x07) + uuid_bytes
        adv_data = flags + service_adv
        resp_data = self._get_device_name_bytes()

        try:
            self._ble.gap_advertise(100_000, adv_data=adv_data, resp_data=resp_data)
            if resp_data:
                name_part = resp_data[2:] if len(resp_data) > 2 else b""
                print(f"[BLE] Broadcasting as '{name_part.decode('utf-8', 'ignore')}'")
            else:
                print("[BLE] Broadcasting without device name")
        except OSError as e:
            print("[BLE] Advertise error:", e)

    def _irq(self, event, data):
        if not self._active:
            return
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self._conn_handle = conn_handle
            self._connected = True
            self._ble.gap_advertise(None)
            print("[BLE] Connected")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            self._conn_handle = None
            self._connected = False
            self._need_restart_adv = True
            print("[BLE] Disconnected")
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle == self._conn_handle and value_handle == self._rx_handle:
                new_data = self._ble.gatts_read(self._rx_handle)
                self._rx_buffer += new_data
                if b"\x04" in new_data:
                    self._ctrl_d_received = True

    def _restart_advertising_if_needed(self):
        if self._need_restart_adv and self._active and not self._connected:
            self._need_restart_adv = False
            self._advertise()

    def _handle_ctrl_d_reset(self):
        print("[BLE] Ctrl+D received, stopping BLE REPL and resetting...")
        try:
            os.dupterm(None)
        except:
            pass
        self.stop()
        time.sleep_ms(100)
        machine.soft_reset()

    def readinto(self, buf):
        while self._active:
            if self._ctrl_d_received:
                self._handle_ctrl_d_reset()

            self._restart_advertising_if_needed()
            if len(self._rx_buffer) > 0:
                n = min(len(buf), len(self._rx_buffer))
                buf[:n] = self._rx_buffer[:n]
                self._rx_buffer = self._rx_buffer[n:]
                return n
            if self._connected:
                time.sleep_ms(10)
            else:
                time.sleep_ms(100)
        return 0

    def write(self, data):
        """分包发送长数据，每包最多20字节，避免截断"""
        if not (self._connected and self._tx_handle is not None):
            return
        CHUNK_SIZE = 20
        for i in range(0, len(data), CHUNK_SIZE):
            chunk = data[i : i + CHUNK_SIZE]
            try:
                self._ble.gatts_notify(self._conn_handle, self._tx_handle, chunk)
                # 微小延时，避免 BLE 堆栈过载
                time.sleep_ms(2)
            except Exception:
                # 连接可能断开，停止发送
                break

    def any(self):
        return len(self._rx_buffer)

    def stop(self):
        if not self._active:
            return
        self._active = False
        try:
            self._ble.gap_advertise(None)
        except:
            pass
        if self._connected and self._conn_handle is not None:
            try:
                self._ble.gap_disconnect(self._conn_handle)
            except:
                pass
        print("[BLE] Service stopped")


_current_uart = None


def start_ble_repl(timeout=30, name=None):
    global _current_uart
    if _current_uart is not None:
        stop_ble_repl()
    ble = bluetooth.BLE()
    uart = BLEUARTStream(ble, name=name)
    _current_uart = uart
    print("[BLE] Advertising...")
    start_time = time.time()
    while not uart._connected:
        if time.time() - start_time > timeout:
            print("[BLE] Connection timeout")
            stop_ble_repl()
            return None
        time.sleep_ms(100)
    print("[BLE] Connected, redirecting REPL...")
    os.dupterm(uart)
    return uart


def stop_ble_repl():
    global _current_uart
    if _current_uart is None:
        print("[BLE] No active BLE REPL service")
        return
    os.dupterm(None)
    _current_uart.stop()
    _current_uart = None
    print("[BLE] BLE REPL stopped, USB REPL restored")
