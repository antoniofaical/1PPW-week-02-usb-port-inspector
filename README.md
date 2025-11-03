# USB Inspector

![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)

**USB Inspector** is a command-line tool written in Python for inspecting USB devices and serial ports. It allows you to list, filter, monitor, and export detailed information about devices connected to your computer, in a clean and interactive way.

> Version: 1.0  
> Author: Antonio Elias Faiçal Jr.

---

## Features

- Scan USB devices using PyUSB
- View detailed device info (VID, PID, manufacturer, serial, etc.)
- Detect and monitor serial ports (COM/ttyUSB)
- Interactive inspection mode with per-device export
- Filter devices by keyword in any field
- JSON output support
- Export results to `.json` or `.txt` files
- CLI-friendly tabular formatting with `tabulate`

---

## Requirements

- Python 3.7+
- Python packages:
  - `pyserial`
  - `pyusb`
  - `tabulate`

```bash
pip install pyserial pyusb tabulate
```

> ⚠️ On Windows, you need to install and configure `libusb` properly.  
> See: https://libusb.info

---

## How to Use

### List connected USB devices

```bash
python usb_inspector.py
```

### Show full device information

```bash
python usb_inspector.py --allinfo
```

### Filter by keyword

```bash
python usb_inspector.py --filter Logitech
```

### Save output to a file

```bash
python usb_inspector.py --allinfo --save usb_output.txt
```

### JSON output

```bash
python usb_inspector.py --json
```

### Interactive inspection mode

```bash
python usb_inspector.py --inspect
```

### Serial port inspection and monitoring

```bash
python usb_inspector.py --serial
```

---

## License

This repository — including all documentation, descriptions, and educational materials —  
is distributed under the  
[**Creative Commons Attribution–NonCommercial 4.0 International License (CC BY-NC 4.0)**](https://creativecommons.org/licenses/by-nc/4.0/).

You are welcome to study, share, and adapt the content for learning purposes.  
Commercial use is not permitted without explicit permission.
