import cv2
import numpy as np
import random
import tkinter as tk
from tkinter import Button, Label, filedialog
from PIL import Image, ImageTk
import time

# Haar Cascade 분류기 파일 경로
face_cascade_path = 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + face_cascade_path)

# Tkinter 창 설정
root = tk.Tk()
root.geometry("640x640+100+100")
root.resizable(True, True)
root.title("Random Face Selector")

# 얼굴 탐지 결과를 표시할 라벨
image_label = Label(root)
image_label.pack()

# 결과를 표시할 라벨
result_label = Label(root, text="", font=("Helvetica", 16))
result_label.pack()

# 얼굴 인식 및 랜덤 선택 변수
detected_faces = []
selected_face = None
image = None
roulette_running = False
start_time = None
cap = None

def load_image():
    global image, detected_faces, selected_face, cap

    if cap:
        cap.release()
        cap = None

    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        if image is not None:
            image = resize_image(image, 640, 400)  # 이미지를 고정된 크기로 리사이즈
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(30, 30))

            detected_faces = []
            for (x, y, w, h) in faces:
                detected_faces.append((x, y, w, h))
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

            display_image(image)
        else:
            result_label.config(text="Error: Could not load image.")
    else:
        result_label.config(text="No image selected.")

def resize_image(image, width, height):
    h, w = image.shape[:2]
    scaling_factor = min(width/w, height/h)
    new_size = (int(w * scaling_factor), int(h * scaling_factor))
    resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return resized_image

def display_image(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    image_label.img_tk = img_tk
    image_label.configure(image=img_tk)

def start_roulette():
    global start_time, roulette_running
    if detected_faces:
        start_time = time.time()
        roulette_running = True
        result_label.config(text="Roulette is running...")
        root.after(100, update_roulette)
        root.after(5000, stop_roulette)  # 5초 후에 룰렛을 멈춥니다.
    else:
        result_label.config(text="No faces detected to start roulette.")

def update_roulette():
    global selected_face
    if roulette_running and detected_faces:
        selected_face = random.choice(detected_faces)
        highlight_selected_face(selected_face[0], selected_face[1], selected_face[2], selected_face[3])
        root.after(100, update_roulette)  # 0.1초마다 업데이트

def stop_roulette():
    global roulette_running
    roulette_running = False
    if selected_face:
        result_label.config(text=f"Final Selected Face: {selected_face}")
        highlight_selected_face(selected_face[0], selected_face[1], selected_face[2], selected_face[3])
        restart_button.pack()  # 재시작 버튼 보이기
    else:
        result_label.config(text="No face selected.")

def highlight_selected_face(x, y, w, h):
    global image
    if image is not None:
        img_copy = image.copy()
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 3)
        display_image(img_copy)

def restart():
    global detected_faces, selected_face, roulette_running, image, cap
    detected_faces = []
    selected_face = None
    roulette_running = False
    image = None
    if cap:
        cap.release()
        cap = None
    result_label.config(text="")
    image_label.config(image='')
    webcam_button.pack()
    restart_button.pack_forget()

def use_webcam():
    global cap, detected_faces, selected_face, roulette_running, image

    if cap:
        cap.release()
        cap = None

    cap = cv2.VideoCapture(1)
    detected_faces = []
    selected_face = None
    roulette_running = False
    result_label.config(text="")
    image_label.config(image='')
    webcam_button.pack_forget()
    detect_faces()

def detect_faces():
    global detected_faces, selected_face, start_time, roulette_running, cap, image

    if cap is not None:
        ret, frame = cap.read()
        if ret:
            frame = resize_image(frame, 640, 400)  # 프레임을 고정된 크기로 리사이즈
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            detected_faces = []
            for (x, y, w, h) in faces:
                detected_faces.append((x, y, w, h))

            if roulette_running:
                # 현재 시간을 기준으로 1초마다 얼굴을 바꿉니다.
                if time.time() - start_time > 1:
                    start_time = time.time()
                    if detected_faces:
                        selected_face = random.choice(detected_faces)
                        result_label.config(text="Selected Face: " + str(selected_face))
                    else:
                        selected_face = None

                # 선택된 얼굴에 바운딩 박스를 그립니다.
                if selected_face:
                    (x, y, w, h) = selected_face
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            else:
                # 얼굴 탐지 결과만 그립니다.
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # 이미지 변환 및 표시
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            image_label.img_tk = img_tk
            image_label.configure(image=img_tk)

        root.after(10, detect_faces)

# Tkinter 버튼
load_button = tk.Button(root, text="Load Image", overrelief="solid", width=15, height=2, command=load_image, repeatdelay=1000, repeatinterval=100)
load_button.pack()

webcam_button = tk.Button(root, text="Use Webcam", overrelief="solid", width=15, height=2, command=use_webcam, repeatdelay=1000, repeatinterval=100)
webcam_button.pack()

roulette_button = tk.Button(root, text="Start Roulette", overrelief="solid", width=15, height=2, command=start_roulette, repeatdelay=1000, repeatinterval=100)
roulette_button.pack()

restart_button = tk.Button(root, text="Restart", overrelief="solid", width=15, height=2, command=restart, repeatdelay=1000, repeatinterval=100)
restart_button.pack_forget()

exit_button = tk.Button(root, text="Exit", overrelief="solid", width=15, height=2, command=root.destroy, repeatdelay=1000, repeatinterval=100)
exit_button.pack()

# 창 닫기 이벤트 처리
def on_closing():
    if cap:
        cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
