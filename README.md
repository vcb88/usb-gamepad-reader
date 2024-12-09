# USB Gamepad Reader

A Python script for reading and displaying input data from a USB gamepad in real-time. The script uses direct USB communication to read button states, joystick positions, triggers, and D-pad states.

## Features

- Real-time display of:
  - Joystick positions (both sticks with accurate percentage values)
  - All button states (A, B, X, Y, L1, R1, Mode, Start, Select)
  - D-pad states with diagonal combinations
  - Analog triggers (L2, R2) with pressure values
  - Special buttons (Turbo, Clear)
- Raw data display for debugging
- Automatic device detection and configuration
- Clean and organized data presentation with auto-updating display

## Hardware Support

Tested with:
- Replica of XBox USB Controller
  - Vendor ID: 0x045e
  - Product ID: 0x028e

Other similar USB gamepads might work but haven't been tested.

## Requirements

- Python 3.7+
- macOS (tested on macOS Sonoma)
- The following dependencies:
  - `libusb` (system library)
  - `pyusb` (Python package)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vcb88/usb-gamepad-reader.git
cd usb-gamepad-reader
```

2. Create and activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Unix-like systems
```

3. Install system dependencies (macOS):
```bash
brew install libusb
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure your gamepad is connected to your computer via USB.

2. Run the script with sudo (required for USB access):
```bash
sudo python gamepad_reader.py
```

3. The script will:
   - List all available USB devices
   - Connect to the gamepad if found
   - Display real-time input data including:
     - Raw data bytes for debugging
     - Interpreted button states
     - Joystick positions in percentages
     - D-pad states including diagonal combinations
     - Trigger values

4. Press Ctrl+C to stop the script.

## Input Data Format

The gamepad sends data packets with the following format:
- Bytes 6-7: Left stick X-axis (big-endian signed 16-bit)
- Bytes 8-9: Left stick Y-axis (big-endian signed 16-bit)
- Bytes 10-11: Right stick X-axis (big-endian signed 16-bit)
- Bytes 12-13: Right stick Y-axis (big-endian signed 16-bit)
- Byte 2 (lower 4 bits): D-pad states (bit mask)
- Byte 2 (upper 4 bits): Start/Select buttons
- Byte 3: Main button states
- Bytes 4-5: Analog triggers
- Byte 14: Special button states

### Stick Values
- 0x0000 = 0% (center)
- 0x8000 = 100% (maximum)
- 0x7FFF = -100% (minimum)

### D-pad Bit Mask
- 0x01: Up
- 0x02: Down
- 0x04: Left
- 0x08: Right
(Combinations create diagonal inputs)

## Troubleshooting

1. If you get a permission error:
   - Make sure to run with sudo
   - Check USB device permissions

2. If the device is not found:
   - Verify the gamepad is properly connected
   - Check if the system recognizes the USB device
   - Confirm the vendor and product IDs match

3. If you get data reading errors:
   - Disconnect and reconnect the gamepad
   - Check for USB conflicts with other devices
   - Try using a different USB port

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

