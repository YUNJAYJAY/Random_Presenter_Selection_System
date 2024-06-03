import cv2
import numpy as np
import random
import tkinter as tk
from tkinter import Button, Label
from PIL import Image, ImageTk
import time

# Haar Cascade 분류기 파일 경로
face_cascade_path = 'haarcascade_frontalface_alt2.xml'
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + face_cascade_path)

# 웹캠 설정
cap = cv2.VideoCapture(1)

# Tkinter 창 설정
root = tk.Tk()
root.title("Random Presenter Selector")

# 얼굴 탐지 결과를 표시할 라벨
video_label = Label(root)
video_label.pack()

# 결과를 표시할 라벨
result_label = Label(root, text="", font=("Helvetica", 16))
result_label.pack()

# 얼굴 인식 및 랜덤 선택 변수
detected_faces = []
selected_face = None
start_time = None
roulette_running = False
stopped = False

def detect_faces():
    global detected_faces, selected_face, start_time, roulette_running, stopped
    if not stopped:
        ret, frame = cap.read()
        if ret:
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
            video_label.img_tk = img_tk
            video_label.configure(image=img_tk)

    root.after(10, detect_faces)

def start_roulette():
    global start_time, roulette_running, stopped
    start_time = time.time()
    roulette_running = True
    stopped = False
    result_label.config(text="Roulette is running...")
    root.after(5000, stop_roulette)  # 5초 후에 룰렛을 멈춥니다.

def stop_roulette():
    global roulette_running, stopped
    roulette_running = False
    stopped = True
    if selected_face:
        result_label.config(text="Final Selected Face: " + str(selected_face))
    else:
        result_label.config(text="No face detected")

def restart():
    global detected_faces, selected_face, start_time, roulette_running, stopped
    detected_faces = []
    selected_face = None
    start_time = None
    roulette_running = False
    stopped = False
    result_label.config(text="")
    start_button.pack()
    restart_button.pack_forget()

# 시작 버튼 클릭 핸들러
def start_detection():
    start_button.pack_forget()  # 시작 버튼 숨기기
    roulette_button.pack()      # 룰렛 버튼 보이기
    detect_faces()

# Tkinter 시작 버튼
start_button = Button(root, text="Start", command=start_detection)
start_button.pack()

# Tkinter 랜덤 선택 버튼
roulette_button = Button(root, text="Start Roulette", command=start_roulette)
roulette_button.pack_forget()

# Tkinter 재시작 버튼
restart_button = Button(root, text="Restart", command=restart)
restart_button.pack_forget()

# 창 닫기 이벤트 처리
def on_closing():
    cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
