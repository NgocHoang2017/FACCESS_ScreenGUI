import cv2
import tkinter as tk
from tkinter import PhotoImage
import PIL.Image, PIL.ImageTk
import time

class NotificationWidget(tk.Toplevel):
    def __init__(self, message):
        super().__init__()

        self.title("Thông báo")
        self.geometry("300x100")

        self.label = tk.Label(self, text=message)
        self.label.pack(fill=tk.BOTH, expand=True)

        self.icon = PhotoImage(file="icon/success.png")
        self.tk.call('wm', 'iconphoto', self._w, self.icon)

    def show(self):
        self.attributes("-alpha", 1.0)
        self.after(3000, self.destroy)  

class FaceDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Detection Application")
        self.root.geometry("640x480")

        self.video_label = tk.Label(root)
        self.video_label.pack()

        self.camera = cv2.VideoCapture(0)
        self.notification_shown = False  

        self.update_frame()

    def detect_face_center(self, gray_img):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return None
        
        max_area_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = max_area_face
        return (x + w // 2, y + h // 2)

    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_center = self.detect_face_center(gray)
            
            if face_center and not self.notification_shown:  
                cv2.circle(frame, face_center, 30, (0, 255, 0), 2)
                self.capture_image()
                notification = NotificationWidget("Chụp ảnh thành công!")
                notification.show()
                self.notification_shown = True  
            
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = PIL.Image.fromarray(rgb_image)
            imgtk = PIL.ImageTk.PhotoImage(image=pil_image)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        self.root.after(30, self.update_frame)

    def capture_image(self):
        current_time = time.time()
        if not hasattr(self, 'last_capture_time'):
            self.last_capture_time = 0
        
        if current_time - self.last_capture_time > 5:
            ret, frame = self.camera.read()
            if ret:
                cv2.imwrite("face.jpg", frame)
                self.last_capture_time = current_time

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceDetectionApp(root)
    root.mainloop()
