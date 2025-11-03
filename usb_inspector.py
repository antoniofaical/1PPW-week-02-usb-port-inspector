"""
USB Inspector v1.0
==================

A cross-platform Python CLI tool to inspect USB devices and serial ports.

Features:
- USB device scanning and display via PyUSB
- Serial port detection with detailed metadata
- Optional serial monitoring with live output
- Filtering by keyword
- JSON output and export
- Tabular CLI-friendly display via `tabulate`
- Interactive inspection mode with per-device save
"""

import sys
import serial
from serial.tools import list_ports
import usb.core
import usb.util
import argparse
import json
from tabulate import tabulate
import usb.backend.libusb1

# Configure DEBUG to print backend info (optional)
DEBUG = False
if DEBUG:
    print(f">> usb backend: {usb.backend.libusb1.get_backend()}")

SEPARATOR = "-" * 80


class USBDevice:
    """
    Represents a single USB device with extracted metadata.
    """

    def __init__(self, device):
        self.vendor_id = device.idVendor
        self.product_id = device.idProduct
        try:
            self.manufacturer = usb.util.get_string(device, device.iManufacturer)
        except:
            self.manufacturer = "Unknown"
        try:
            self.product = usb.util.get_string(device, device.iProduct)
        except:
            self.product = "Unknown"
        try:
            self.serial = usb.util.get_string(device, device.iSerialNumber)
        except:
            self.serial = "Unknown"

    def to_dict(self):
        """
        Converts device metadata to a dictionary.
        """
        return {
            "VID": hex(self.vendor_id),
            "PID": hex(self.product_id),
            "Manufacturer": self.manufacturer,
            "Product": self.product,
            "Serial": self.serial
        }

    def matches_filter(self, keyword):
        """
        Checks if the keyword is present in any of the device's fields.
        """
        keyword = keyword.lower()
        return any(keyword in str(value).lower() for value in self.to_dict().values())


def scan_usb_devices():
    """
    Scans and returns a list of connected USB devices.
    """
    return [USBDevice(dev) for dev in usb.core.find(find_all=True)]


def list_serial_ports():
    """
    Lists available serial ports and prints them with descriptions.
    """
    ports = list(list_ports.comports())
    if not ports:
        print("\n   >> No serial devices detected.\n")
        return []
    print("\n   Ports available for inspection:\n")
    for i, port in enumerate(ports):
        print(f"   [{i+1}] {port.device}\t{port.description}")
    return ports


def get_serial_port_info(port_name):
    """
    Retrieves and prints detailed metadata for the selected serial port.
    """
    for port in list_ports.comports():
        if port.device == port_name:
            print(f"\n{SEPARATOR}")
            print("   Device information:")
            print(f"   Name:          {port.name}")
            print(f"   Device:        {port.device}")
            print(f"   Description:   {port.description}")
            print(f"   Manufacturer:  {port.manufacturer}")
            print(f"   HWID:          {port.hwid}")
            print(f"   VID:PID:       {port.vid}:{port.pid}")
            print(f"   Location:      {port.location}")
            print(SEPARATOR)
            return port
    print(f"\n   >> Port '{port_name}' not found.")
    return None


def read_serial_data(port_name, baudrate=115200):
    """
    Opens a serial connection and prints live data output from the device.
    """
    try:
        ser = serial.Serial(port_name, baudrate, timeout=1)
        print(f"\nListening to {port_name} at {baudrate} baud...\n")
        print("Press Ctrl+C to stop.\n")
        while True:
            if ser.in_waiting:
                data = ser.readline().decode(errors='ignore').strip()
                print(data)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except serial.SerialException as e:
        print(f"   >> Serial error: {e}")
    except Exception as e:
        print(f"   >> Unexpected error: {e}")
    finally:
        try:
            ser.close()
        except:
            pass


def interactive_inspect(devices):
    """
    Allows user to interactively explore connected USB devices.
    """
    while True:
        print("\nDetected USB Devices:\n")
        for i, dev in enumerate(devices):
            print(f"[{i+1}] {dev.product} ({hex(dev.vendor_id)}:{hex(dev.product_id)})")

        choice = input("\nEnter the number of the device to inspect ('q' to quit): ").strip()
        if choice.lower() == 'q':
            print("\nExiting interactive mode...\n")
            break

        if not choice.isdigit() or not (1 <= int(choice) <= len(devices)):
            print("Invalid selection. Please try again.")
            continue

        selected = devices[int(choice) - 1]
        print("\n" + json.dumps(selected.to_dict(), indent=4) + "\n")

        save = input("Would you like to save this device info to JSON? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"usb_device_{selected.vendor_id:04x}_{selected.product_id:04x}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(selected.to_dict(), f, indent=4)
            print(f"\n   >> Device info saved to {filename}\n")


def main():
    parser = argparse.ArgumentParser(description=f"{SEPARATOR} USB Inspector CLI Tool {SEPARATOR}")
    parser.add_argument("--allinfo", action="store_true", help="Show full USB device info")
    parser.add_argument("--filter", type=str, help="Filter results by keyword")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--save", type=str, help="Save output to file")
    parser.add_argument("--serial", action="store_true", help="Enter serial port inspector mode")
    parser.add_argument("--inspect", action="store_true", help="Interactive inspection mode")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        print("\n")
        sys.exit(0)

    if args.serial:
        while True:
            ports = list_serial_ports()
            if not ports:
                return

            user_input = input("\n  Choose a port (number or name, or 'q' to return): ").strip()
            if user_input.lower() == 'q':
                break
            if user_input.isdigit() and 1 <= int(user_input) <= len(ports):
                selected = ports[int(user_input) - 1].device
            else:
                selected = user_input

            info = get_serial_port_info(selected)
            if not info:
                continue

            read = input("\n   >> Read data from this port? (y/n): ").strip().lower()
            if read == 'y':
                read_serial_data(selected)

    print(SEPARATOR)
    print("\nUSB Inspector (v1.0)")
    print("Scanning USB devices...\n")
    print(SEPARATOR)

    devices = scan_usb_devices()
    if args.filter:
        devices = [d for d in devices if d.matches_filter(args.filter)]

    if args.inspect:
        interactive_inspect(devices)
        return

    if args.json:
        output = json.dumps([d.to_dict() for d in devices], indent=4)
    elif args.allinfo:
        table = [d.to_dict() for d in devices]
        output = tabulate(table, headers="keys")
    else:
        table = [[hex(d.vendor_id), hex(d.product_id), d.product] for d in devices]
        output = tabulate(table, headers=["VID", "PID", "Product"])

    print("\n" + output + "\n")

    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\n   >> Output saved to {args.save}\n")


if __name__ == "__main__":
    main()
