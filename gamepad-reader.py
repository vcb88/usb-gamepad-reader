import sys
import time
import os
import usb.core
import usb.util
from usb.backend import libusb1

class GamePadReader:
    def __init__(self):
        self.vendor_id = 0x045e  # Microsoft Corporation
        self.product_id = 0x028e  # Controller
        self.device = None
        self.endpoint = None
        
        # Find libusb on macOS
        lib_path = '/opt/homebrew/lib/libusb-1.0.dylib'
        if os.path.exists(lib_path):
            print(f"Found libusb at: {lib_path}")
            self.backend = libusb1.get_backend(find_library=lambda x: lib_path)
        else:
            print("Could not find libusb library!")
            self.backend = None

    def find_device(self):
        """Find our specific gamepad"""
        if not self.backend:
            print("No USB backend available!")
            return False
            
        print(f"Looking for device (Vendor ID: 0x{self.vendor_id:04x}, Product ID: 0x{self.product_id:04x})...")
        
        # Find our specific device
        self.device = usb.core.find(
            idVendor=self.vendor_id,
            idProduct=self.product_id,
            backend=self.backend
        )
        
        if self.device is None:
            print("\nTarget device not found!")
            return False
            
        print("\nDevice found!")
        return True

    def setup_device(self):
        """Setup the device for communication"""
        if self.device is None:
            return False
            
        try:
            print(f"\nDevice information:")
            print(f"Bus: {self.device.bus}")
            print(f"Address: {self.device.address}")
            
            # Set configuration
            self.device.set_configuration()
            
            # Find the interrupt IN endpoint
            cfg = self.device.get_active_configuration()
            for intf in cfg:
                print(f"\nInterface {intf.bInterfaceNumber}:")
                for ep in intf:
                    print(f"  Endpoint 0x{ep.bEndpointAddress:02x}:")
                    print(f"  Direction: {'IN' if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else 'OUT'}")
                    print(f"  Attributes: 0x{ep.bmAttributes:02x}")
                    print(f"  Max packet size: {ep.wMaxPacketSize}")
                    
                    # We're looking for interrupt IN endpoint
                    if (usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN and 
                        ep.bmAttributes & 0x03 == usb.util.ENDPOINT_TYPE_INTR):
                        self.endpoint = ep
                        print("  Using this endpoint for input")
            
            if not self.endpoint:
                print("Could not find suitable endpoint")
                return False

            print("\nDevice setup complete")
            return True

        except usb.core.USBError as e:
            print(f"USB Error during setup: {str(e)}")
            return False
        except Exception as e:
            print(f"Error setting up device: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def process_data(self, data):
        """Precise data processing with accurate byte mapping"""
        if not data:
            return

        # Clear screen and print raw data for reference
        print("\033[2J\033[H")  # Clear screen
        print("Raw data:", ' '.join([f"{x:02x}" for x in data]))
        print("-" * 60)

        try:
            # Crosskey (byte 2)
            crosskey_map = {
                1: "Up", 
                2: "Down", 
                4: "Left", 
                8: "Right",
                9: "Up-Right",     # Added
                6: "Down-Left",    # Added
                3: "Up-Left", 
                5: "Down-Right"    # Added
            }
            crosskey_byte = data[2] & 0x0F  # Lower 4 bits
            if crosskey_byte in crosskey_map:
                print(f"Crosskey: {crosskey_map[crosskey_byte]}")

            # Buttons (bytes 2 and 3)
            button_map_byte2 = {
                0x10: "Start",
                0x20: "Select"
            }
            button_map_byte3 = {
                0x01: "L1",
                0x02: "R1", 
                0x04: "Mode",
                0x10: "A",
                0x20: "B",
                0x40: "X", 
                0x80: "Y"
            }

            # Analyze buttons
            buttons_pressed = []
            for bit, name in button_map_byte2.items():
                if data[2] & bit:
                    buttons_pressed.append(name)
            for bit, name in button_map_byte3.items():
                if data[3] & bit:
                    buttons_pressed.append(name)
            
            print("Buttons pressed:", ", ".join(buttons_pressed) if buttons_pressed else "None")

            # Stick interpretation function
            def interpret_stick_axis(low_byte, high_byte):
                """
                Interpret stick axis with specific range handling
                - 0x0000 to 0x0080: Negative direction
                - 0x0000 to 0xff7f: Positive direction
                """
                value = (high_byte << 8) | low_byte
                
                # Negative direction (left/down)
                if value <= 0x0080:
                    return -((0x0080 - value) / 0x0080) * 100
                
                # Positive direction (right/up)
                elif value >= 0xff7f:
                    return ((value - 0xff7f) / 0x0080) * 100
                
                # Neutral position
                return 0

            # Left Stick
            left_stick_x = interpret_stick_axis(data[6], data[7])
            left_stick_y = interpret_stick_axis(data[8], data[9])
            print(f"Left Stick: X: {left_stick_x:6.1f}% | Y: {left_stick_y:6.1f}%")

            # Right Stick  
            right_stick_x = interpret_stick_axis(data[10], data[11])
            right_stick_y = interpret_stick_axis(data[12], data[13])
            print(f"Right Stick: X: {right_stick_x:6.1f}% | Y: {right_stick_y:6.1f}%")

            # Triggers
            print(f"L2 Trigger: {data[4]/255:6.1%}")
            print(f"R2 Trigger: {data[5]/255:6.1%}")

            # Additional special buttons
            special_buttons = []
            if data[14] & 0x20:
                special_buttons.append("Turbo")
            if data[14] & 0x40:
                special_buttons.append("Clear")
            
            if special_buttons:
                print("Special Buttons:", ", ".join(special_buttons))

        except Exception as e:
            print(f"Error processing data: {e}")
            import traceback
            traceback.print_exc()

    def read_input(self):
        """Read and process input from the gamepad"""
        if not self.endpoint:
            print("Device not properly set up")
            return

        print("\nReading input data... Press Ctrl+C to stop.")
        
        try:
            while True:
                try:
                    # Read data from the endpoint
                    data = self.device.read(self.endpoint.bEndpointAddress, 
                                          self.endpoint.wMaxPacketSize,
                                          timeout=100)
                    if data:
                        self.process_data(data)
                except usb.core.USBTimeoutError:
                    continue  # Normal timeout, just continue
                except usb.core.USBError as e:
                    if e.args[0] == 110:  # Operation timed out
                        continue
                    else:
                        print(f"USB Error: {str(e)}")
                        break
                
                time.sleep(0.1)  # Small delay to prevent CPU overload
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            # Release the interface
            if self.device:
                try:
                    usb.util.release_interface(self.device, 0)
                except:
                    pass

def main():
    reader = GamePadReader()
    
    if not reader.find_device():
        print("Device not found!")
        sys.exit(1)
        
    if not reader.setup_device():
        print("Failed to setup device!")
        sys.exit(1)
        
    reader.read_input()

if __name__ == "__main__":
    main()
