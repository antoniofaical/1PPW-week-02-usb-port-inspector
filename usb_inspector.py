import sys
import serial
from serial.tools import list_ports
import usb.core
import usb.util

SEPARATOR = "-" * 100


def list_all_usb_devices():
    """List every USB device recognized by the system."""
    print("\nConnected USB devices:\n")
    devices = usb.core.find(find_all=True)
    if not devices:
        print("   >> No USB devices detected.")
        return
    for i, dev in enumerate(devices, 1):
        print(f"[{i}] VID:PID = {hex(dev.idVendor)}:{hex(dev.idProduct)}")
        try:
            manufacturer = usb.util.get_string(dev, dev.iManufacturer)
        except:
            manufacturer = "Unknown"
        try:
            product = usb.util.get_string(dev, dev.iProduct)
        except:
            product = "Unknown"
        try:
            serial = usb.util.get_string(dev, dev.iSerialNumber)
        except:
            serial = "Unknown"
        print(f"     Manufacturer: {manufacturer}")
        print(f"     Product:      {product}")
        print(f"     Serial:       {serial}\n")


def list_available_ports():
    """Lists all available serial ports and returns them as a list."""
    ports = list(list_ports.comports())
    if not ports:
        print("\n   >> No serial devices detected.\n")
        return []
    print("\n   Ports available for inspection:\n")
    for i, port in enumerate(ports):
        print(f"   [{i+1}] {port.device}\t{port.description}")
    return ports


def get_port_info(port_name):
    """Displays detailed information about a given port."""
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


def read_serial(port_name, baudrate=115200):
    """Opens a serial connection and reads incoming data in real-time."""
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
    """Main program loop for the USB Port Inspector CLI."""
    print("\n", SEPARATOR)
    print("   USB Port Inspector (v0.3)")
    print("   Inspect USB peripherals connected to your system.")

    while True:
        try:
            print("\n", SEPARATOR)
            print("\n   Options:\n")
            print("     [1] List serial devices (COM / ttyUSB)")
            print("     [2] List all USB devices")
            print("     [q] Quit")

            choice = input("\nChoose an option: ").strip().lower()

            if choice == '1':

                ports = list_available_ports()
                if not ports:
                    continue

                user_input = input("\n  Choose a port (number or name): ").strip()

                # Allow selection by index or by name (COMx, /dev/ttyUSBx, etc.)
                if user_input.isdigit() and 1 <= int(user_input) <= len(ports):
                    selected_port = ports[int(user_input) - 1].device
                else:
                    selected_port = user_input

                port_info = get_port_info(selected_port)
                if not port_info:
                    continue

                # Ask if user wants to open serial monitor
                choice = input("\n   >> Read data from this port? (y/n): ").strip().lower()
                if choice == 'y':
                    read_serial(selected_port)

            elif choice == '2':
                list_all_usb_devices()
            elif choice == 'q':
                print("\nExiting program...\n")
                break
            else:
                print("Invalid option. Try again.")



        except KeyboardInterrupt:
            print("\n\n   >> Interrupted by user. Exiting...\n")
            break
        except Exception as e:
            print(f"\n   >> Unexpected error: {e}")
            break


if __name__ == "__main__":
    main()
