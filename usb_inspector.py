"""
USB Inspector v0.4
Now with:
 - USBDevice class abstraction
 - CLI-friendly tabular output
 - Optional JSON export
 - Filtering by keyword
 - Separated core logic from CLI prompts
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

# Configure DEBUG as fit
DEBUG = False
if DEBUG:
    print(f">> usb backend: {usb.backend.libusb1.get_backend()}") 

SEPARATOR = "-" * 100



class USBDevice:
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
        return {
            "VID": hex(self.vendor_id),
            "PID": hex(self.product_id),
            "Manufacturer": self.manufacturer,
            "Product": self.product,
            "Serial": self.serial
        }

    def matches_filter(self, keyword):
        keyword = keyword.lower()
        return any(keyword in str(value).lower() for value in self.to_dict().values())


def scan_usb_devices():
    return [USBDevice(dev) for dev in usb.core.find(find_all=True)]


def list_serial_ports():
    ports = list(list_ports.comports())
    if not ports:
        print("\n   >> No serial devices detected.\n")
        return []
    print("\n   Ports available for inspection:\n")
    for i, port in enumerate(ports):
        print(f"   [{i+1}] {port.device}\t{port.description}")
    return ports


def get_serial_port_info(port_name):
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


def main():
    parser = argparse.ArgumentParser(description="USB Inspector CLI Tool")
    parser.add_argument("--allinfo", action="store_true", help="Show full USB device info")
    parser.add_argument("--filter", type=str, help="Filter results by keyword")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--save", type=str, help="Save output to file")
    parser.add_argument("--serial", action="store_true", help="Enter serial port inspector mode")

    args = parser.parse_args()

    if args.serial:
        ports = list_serial_ports()
        if not ports:
            sys.exit(0)
        user_input = input("\n  Choose a port (number or name): ").strip()
        if user_input.isdigit() and 1 <= int(user_input) <= len(ports):
            selected = ports[int(user_input) - 1].device
        else:
            selected = user_input
        info = get_serial_port_info(selected)
        if info:
            read = input("\n   >> Read data from this port? (y/n): ").strip().lower()
            if read == 'y':
                read_serial_data(selected)
        sys.exit(0)

    print("\n   USB Inspector (v0.4)")
    print("   Scanning USB devices...\n")

    devices = scan_usb_devices()
    if args.filter:
        devices = [d for d in devices if d.matches_filter(args.filter)]

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
