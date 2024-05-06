import cv2
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QRect, QEasingCurve, QPropertyAnimation

class NotificationWidget(QWidget):
    def __init__(self, message):
        super().__init__()

        self.setWindowTitle("Thông báo")
        self.setGeometry(600, 400, 300, 100)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)

        # Animation properties
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)  # Animation duration in milliseconds
        self.animation.setStartValue(QRect(600, 400, 300, 0))
        self.animation.setEndValue(QRect(600, 400, 300, 100))
        self.animation.setEasingCurve(QEasingCurve.OutBounce)

        # Set icon for the window
        self.setWindowIcon(QIcon("icon/success.png"))
        # Start animation
        self.animation.start()

        # Set up timer to close the notification after 1 second
        QTimer.singleShot(1000, self.close)

    def close(self):
        # Animation to fade out and close the notification
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(600, 400, 300, 100))
        self.animation.setEndValue(QRect(600, 400, 300, 0))
        self.animation.setEasingCurve(QEasingCurve.InBack)
        self.animation.finished.connect(super().close)
        self.animation.start()

class FaceDetectionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Face Detection Applicatinon")
        self.setFixedSize(1920, 1080)

        self.video_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)

        self.setLayout(layout)

        self.camera = cv2.VideoCapture(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.countdown)
        self.count = 3

        self.capture_done = False

    def detect_face_center(self, gray_img):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return None
        
        max_area_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = max_area_face
        return (x + w // 2, y + h // 2)

    def countdown(self):
        self.count -= 1
        if self.count == 0:
            self.countdown_timer.stop()
            self.capture_done = True
            self.count = 3
            self.save_image()

    def update_frame(self):
        ret, frame = self.camera.read()
        if not ret:
            return
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        face_center = self.detect_face_center(gray)
        
        if face_center and not self.capture_done:
            cv2.circle(frame, face_center, 30, (0, 255, 0), 2)
            if not self.countdown_timer.isActive():
                self.countdown_timer.start(1000)
        
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.video_label.setPixmap(pixmap)

    def save_image(self):
        ret, frame = self.camera.read()
        if not ret:
            return
        cv2.imwrite("face.jpg", frame)
        self.show_success_notification("Chụp ảnh thành công!")

    def show_success_notification(self, message):
        notification = NotificationWidget(message)
        notification.show()

    def closeEvent(self, event):
        self.timer.stop()
        self.countdown_timer.stop()
        self.camera.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    display = FaceDetectionApp()
    display.show()
    sys.exit(app.exec_())
