import numpy as np
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.clock import Clock
from pyzbar.pyzbar import decode
import cv2

class BarcodeScannerApp(App):

    def __init__(self, on_scan_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_scan_callback = on_scan_callback

    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Kivy Camera widget for displaying the video feed
        self.camera = Camera(play=True, resolution=(640, 480), size_hint=(1, 0.8))
        layout.add_widget(self.camera)

        # Label to display scanned barcode results
        self.scanning_label = Label(text="Scanning...", size_hint=(1, 0.2))
        layout.add_widget(self.scanning_label)

        # Variable to store the last scanned barcode
        self.last_scanned_barcode = None

        # Flag to control scanning
        self.scanning_enabled = True

        # Schedule a function to process frames from the camera every 1/30 seconds
        Clock.schedule_interval(self.process_frame, 1.0 / 30.0)

        return layout

    def process_frame(self, dt):
        # If scanning is disabled, return early
        if not self.scanning_enabled:
            return

        # Get the current frame from the camera
        texture = self.camera.texture

        # If the camera texture is not ready, return early
        if not texture:
            return

        # Convert the texture data (pixels) into a NumPy array
        frame = np.frombuffer(texture.pixels, np.uint8).reshape(texture.height, texture.width, 4)

        # Convert RGBA to RGB
        frame = frame[:, :, :3]

        # Convert the frame to grayscale, as pyzbar works best on grayscale images
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Decode barcodes in the frame using pyzbar
        barcodes = decode(gray_frame)

        if barcodes:
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type
                self.scanning_label.text = f"Scanned: {barcode_data} ({barcode_type})"

                # Update the last scanned barcode variable
                self.last_scanned_barcode = barcode_data

                print(f"Detected barcode: {barcode_data}, Type: {barcode_type}")

                # Disable further scanning
                self.scanning_enabled = False

                # Schedule a delay before re-enabling scanning (e.g., 3 seconds)
                Clock.schedule_once(self.enable_scanning, 3)
                self.process_barcode()

                return  # Exit the loop after the first barcode is detected

        else:
            self.scanning_label.text = "Scanning..."

    def enable_scanning(self, dt):
        """Function to re-enable scanning after a delay."""
        self.scanning_enabled = True

    def get_last_scanned_barcode(self):
        """Function to retrieve the last scanned barcode."""
        return self.last_scanned_barcode

    def process_barcode(self):

        barcode = self.last_scanned_barcode
        order_number = barcode[:10]
        print(order_number)
        line_number = ""
        remaining_barcode = ""
        if "-" in barcode:
            line_number = barcode[10:]
            print(line_number)
        else:
            remaining_barcode = barcode[10:]
            print(remaining_barcode)

        self.processed_barcode = {
            barcode:
                {
            "order number": order_number,
            "line number": line_number,
            "CID": remaining_barcode
            }
        }

        print(self.processed_barcode)
        return self.processed_barcode

    def close_scanner(self):
        # Stop the camera or scanning process here
        if self.camera:  # Assuming camera object exists
            self.camera.stop()

        # Return to the main screen
        self.manager.current = 'main'  # Assuming 'main' is the name of the main screen


if __name__ == '__main__':
    BarcodeScannerApp().run()
