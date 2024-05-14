import sys
import cv2
import numpy as np
import threading
import logging
import serial
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QDesktopWidget, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
import sqlite3
from datetime import datetime
import socket
from urllib.parse import urlparse, parse_qs

# Setup logging
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# Load the haarcascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Command
CMD_DETECT_OBJ = 0x10

class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().__init__(parent)
        self.setWindowTitle("Camera Widget")
        self.resize(800, 600)  
        self.center_on_screen()
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)

        # Initialize the camera
        self.capture = cv2.VideoCapture(1)

        # Create a timer for updating the camera stream
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000/15))  # 15 fpf
        
        # Flag for capturing image
        self.capture_image = False

    def center_on_screen(self):
        # Get the screen geometry
        screen_geometry = QDesktopWidget().screenGeometry()
        # Calculate the center point
        center_point = screen_geometry.center()
        # Move the widget to the center
        self.move(center_point - self.rect().center())

    def update_frame(self):
        try:
            ret, frame = self.capture.read()
            if ret:
                # Convert from OpenCV image to QImage
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                # Display the image on label
                self.image_label.setPixmap(pixmap)
                
                # Check if image capture is requested
                if self.capture_image:
                    self.capture_image = False
                    capture_and_save_image(frame)
        except Exception as e:
            logging.error("Error occurred while capturing frame: %s", e)

    def closeEvent(self, event):
        # Stop the timer and release the camera when the widget is closed
        self.timer.stop()
        self.capture.release()
        event.accept()

def serial_reader():
    # Open the serial port
    with serial.Serial('/dev/ttyAML1', 115200, timeout=1) as ser:
        while True:
            data = ser.readline()
            if data:
                # Process the received data from the serial port
                logging.debug("Data from serial: %s", data)
                if data[2] == CMD_DETECT_OBJ:
                    camera_widget.capture_image = True
                    send_serial_response(ser,0x00)
                    

def send_serial_response(ser, message):
    """Send a response to the serial port."""
    try:
        ser.write(bytes([message]))  
        logging.debug("Status: 0x%02x", message)
    except Exception as e:
        logging.error("Error sending response via serial: %s", e)
        
def capture_and_save_image(frame):
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    # If faces are detected
    if len(faces) > 0:
        # Choose the nearest face to the center of the image
        reference_point = (frame.shape[1] // 2, frame.shape[0] // 2)
        nearest_face = min(faces, key=lambda face: ((reference_point[0] - (face[0] + face[2] // 2)) ** 2 + (reference_point[1] - (face[1] + face[3] // 2)) ** 2) ** 0.5)
        x, y, w, h = nearest_face
        
        # Crop and resize the face
        cropped_face = frame[y:y+h, x:x+w]
        cropped_face = cv2.resize(cropped_face, (300, 400))
        
        # Convert to binary
        _, buffer = cv2.imencode('.jpg', cropped_face)
        binary_image = buffer.tobytes()
        
        # Save the image to SQLite database
        try:
            conn = sqlite3.connect('face.db')
            cursor = conn.cursor()
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO Images (Date, Time, Image) VALUES (?, ?, ?)", (date_time, date_time, sqlite3.Binary(binary_image)))
            conn.commit()
            logging.debug("Image inserted database successfully!")
            show_message_box("Success", "Capture image successfully")
        except sqlite3.Error as e:
            logging.error("Error inserting image to database: %s", e)
            show_message_box("Error", "Error")
        finally:
            if conn:
                conn.close()
    else:
        logging.warning("No face detected!")


def show_message_box(title, message, icon=QMessageBox.Information):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(icon)

    QTimer.singleShot(1000, msg.close)
    msg.exec_()

def process_request(request, client_socket):
    """Process the client request and send a response back."""
    parsed_url = urlparse(request)
    query_params = parse_qs(parsed_url.query)
    
    if 'message' in query_params:
        # Get the value of the message parameter
        message_value = query_params.get('message', [''])[0]
        capture_value = message_value.split(' ')[0]
    
        # Check if the message is 'capture'
        if capture_value == 'capture':
            # Call a function to handle the capture process
            camera_widget.capture_image = True
            send_response(client_socket, "Success")
            logging.info("Image capture request received.")
        else:
            send_response(client_socket, "Error")
            logging.warning("Invalid command.")
    else:
        send_response(client_socket, "Error")
        logging.error("Unavalble message.")  
    

def send_response(client_socket, message):
    """Send a response to the client with the given message."""
    try:
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(message)}\r\n\r\n{message}"
        client_socket.sendall(response.encode())
    except Exception as e:
        logging.error("Error sending response: %s", e)
      
def start_server():
    """Start the socket server and listen for incoming connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.1.140', 8000)
    server_socket.bind(server_address)
    server_socket.listen(1)
    
    server_address = server_socket.getsockname()
    logging.info("Server address: %s:%s", server_address[0], server_address[1])
    
    
    while True:
        client_socket, client_address = server_socket.accept()
        logging.info("Connected to client: %s", client_address)
        try:
            data = client_socket.recv(1024).decode()
            process_request(data, client_socket)
        except Exception as e:
            logging.error("Error processing client request: %s", e)
        finally:
            client_socket.close()
            logging.info("Connection closed.")



def main():
    # Create threads for serial port and socket server
    serial_thread = threading.Thread(target=serial_reader)
    serial_thread.start()

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    camera_widget = CameraWidget()
    camera_widget.showFullScreen()
    main_thread = threading.Thread(target=main)
    main_thread.start()
    sys.exit(app.exec_())
