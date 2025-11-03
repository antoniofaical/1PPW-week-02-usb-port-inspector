# import ...
from serial.tools import list_ports

SEPARATOR = "-" * 100

def ports_listing():
    ports = list_ports.comports()
    for p in ports:
        print(f"{p.device}\t{p.description}")


def get_port_info(port_name):
    for port in list_ports.comports():
        if port.device == port_name:
            print(f"\nDevice info:")
            print(f"Name: {port.name}")
            print(f"Description: {port.description}")
            print(f"Manufacturer: {port.manufacturer}")
            print(f"VID: {port.vid}")
            print(f"PID: {port.pid}")
            return port
    print("\n   >> Port not found.")
    return None


def main ():
    """Main program loop for the USB Port Inspector CLI."""
    print("\n", SEPARATOR)
    print("\n   Welcome to the USB Port Inspector! This program helps you inspect your USB ports!\n")
    
    print("\n   Ports available for inspecting:\n")
    ports_listing()

    while True:
        try: 
            print("\n", SEPARATOR, "\n")
            user_input = input("\n  Choose the port: ")

            get_port_info(user_input)
        except:
            print("\n\n", SEPARATOR, "\n")
            print("Quitting progam...\n")
            break


if __name__ == "__main__": 
    main()
