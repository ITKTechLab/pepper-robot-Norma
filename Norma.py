# -*- coding: utf-8 -*-
import os
import time
import socket
import threading
import SimpleHTTPServer
import SocketServer
from naoqi import ALProxy
import pygame
import cv2
import numpy as np

# ===================================================================
# Trin 1: Find billedfilen til tabletvisning
# ===================================================================
LOCAL_IMAGE_PATH = r"C:\Users\fohre\Desktop\Billeder_til_Norma\Norma_Velkommen.png"
if not os.path.exists(LOCAL_IMAGE_PATH):
    raise IOError("Billedfil ikke fundet: %s" % LOCAL_IMAGE_PATH)

# ===================================================================
# Trin 2: Initialiser NAOqi-proxies
# ===================================================================
IP        = "192.168.1.155"
PORT      = 9559
arm_mode  = False

motion    = ALProxy("ALMotion",          IP, PORT)
tts       = ALProxy("ALTextToSpeech",    IP, PORT)
animation = ALProxy("ALAnimationPlayer", IP, PORT)
tablet    = ALProxy("ALTabletService",   IP, PORT)
video     = ALProxy("ALVideoDevice",     IP, PORT)

# ===================================================================
# Trin 3: Start simpel HTTP‐server og load billedet via HTTP
# ===================================================================
def start_file_server(root, port=8000):
    os.chdir(root)
    handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", port), handler)
    httpd.serve_forever()

# Find en IP på din PC, som Norma‐robotten kan nå
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))
    pc_ip = s.getsockname()[0]
finally:
    s.close()

# Start HTTP-server i baggrundstråd (Python2-venlig)
root_folder = os.path.dirname(LOCAL_IMAGE_PATH)
server_thread = threading.Thread(
    target=start_file_server,
    args=(root_folder, 8000)
)
server_thread.setDaemon(True)
server_thread.start()
time.sleep(1)  # giv serveren tid til at starte

# Byg URL til billedet
filename = os.path.basename(LOCAL_IMAGE_PATH)
url = "http://%s:8000/%s" % (pc_ip, filename)

# Vis billedet på Norma’s tablet
tablet.hideWebview()
tablet.loadUrl(url)
time.sleep(0.5)
tablet.showWebview()

# Leg lidt med animation og tale
animation.runTag("cloud")
tts.say("Jeg hedder Norma og jeg funker")

# ===================================================================
# Trin 4: Kamera-stream & ansigtsdetektion
# ===================================================================
resolution   = 1
color_space  = 13
fps          = 10
camera_name  = "camera_top"
video_client = video.subscribeCamera(camera_name, 0, resolution, color_space, fps)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

motion.setStiffnesses("Head", 1.0)
motion.wbEnable(False)

def get_camera_frame():
    image = video.getImageRemote(video_client)
    if image:
        w, h = image[0], image[1]
        return np.fromstring(image[6], dtype=np.uint8).reshape((h, w, 3))
    return None

def detect_faces(frame):
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30,30))
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
    return frame

# ===================================================================
# Trin 5: Joystick-input & knapper
# ===================================================================
def process_joystick_input(js):
    pygame.event.pump()
    x, y       = js.get_axis(0),    -js.get_axis(1)
    yaw, pitch = js.get_axis(2),    -js.get_axis(3)
    thr        = 0.2
    x     = 0 if abs(x)     < thr else x
    y     = 0 if abs(y)     < thr else y
    yaw   = 0 if abs(yaw)   < thr else yaw
    pitch = 0 if abs(pitch) < thr else pitch

    ms, hs = 0.5, 0.2
    motion.move(y * ms, 0, x * ms)
    cy = motion.getAngles("HeadYaw",   True)[0]
    cp = motion.getAngles("HeadPitch", True)[0]
    motion.setAngles(
        ["HeadYaw","HeadPitch"],
        [np.clip(cy + yaw   * hs, -2.0,  2.0),
         np.clip(cp + pitch * hs, -0.5,  0.5)],
        0.1
    )

def process_joystick_buttons(js):
    global arm_mode
    if js.get_button(7):
        arm_mode = not arm_mode
        tts.say("Nu kan du styre mine arme" if arm_mode else "Nu styrer jeg selv mine arme")
        pygame.time.wait(500)

    if arm_mode:
        left, right = "LShoulderPitch", "RShoulderPitch"
        step, sens  = 0.05, 0.1
        la = motion.getAngles(left,  True)[0]
        ra = motion.getAngles(right, True)[0]

        if js.get_button(4):
            motion.setAngles(left,  max(-1.5, la - step), 0.05)
        if js.get_button(5):
            motion.setAngles(right, max(-1.5, ra - step), 0.05)

        lt = js.get_axis(4)
        if lt > 0.1:
            motion.setAngles(left, min(1.5, la + lt * sens), 0.05)
        rt = js.get_axis(5)
        if rt > 0.1:
            motion.setAngles(right, min(1.5, ra + rt * sens), 0.05)
    else:
        if js.get_button(0):
            animation.runTag("hello")
            tts.say("Jeg hedder Norma, jeg elsker kage")
        if js.get_button(1):
            animation.runTag("crazy")
            tts.say("Prutbanan")
        if js.get_button(2):
            animation.runTag("enthusiastic")
            tts.say("Du ligner en der har sure tæer")
        if js.get_button(3):
            animation.runTag("agitated")
            tts.say("Jeg hedder Norma og jeg elsker prutbananer")
        if js.get_button(7):
            animation.runtag("hello")
            tts.say("Velkommen til biblioteket, jeg hedder Norma, hvad hedder du")
        if js.get_button(14):
            animation.runtag("hello")
            tts.say("Hej fru prutbanan")
        if js.get_button(13):
            animation.runtag("hello")
            tts.say("Hej hr prutbanan")
        if js.get_button(12):
            animation.runtag("hello")
            tts.say("Hej din gigantiske prutbanan")
        pygame.time.wait(1500)

# ===================================================================
# Trin 6: Main-loop & cleanup
# ===================================================================
def main():
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("Ingen controller fundet")
        return
    js = pygame.joystick.Joystick(0)
    js.init()
    print("Controller tilsluttet:", js.get_name())

    cv2.namedWindow("Norma Kamera", cv2.WINDOW_AUTOSIZE)

    try:
        while True:
            frame = get_camera_frame()
            if frame is not None:
                frame = detect_faces(frame)
                cv2.imshow("Norma Kamera", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            process_joystick_input(js)
            process_joystick_buttons(js)

    except KeyboardInterrupt:
        print("Stopper...")
        motion.stopMove()
    finally:
        pygame.quit()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
