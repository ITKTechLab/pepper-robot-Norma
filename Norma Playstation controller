#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
# Tjek at vi kører Python 2.7
if sys.version_info[0] != 2:
    print("Dette script kræver Python 2.7")
    sys.exit(1)

# Importér nødvendige biblioteker
import base64          # Til kodning af billede til base64
import time            # Til tidsstyring (sleep)
import cv2             # OpenCV til videostreaming og ansigtsdetektion
import numpy as np     # Til billedarray-håndtering
import pygame          # Til joystick-input og visualisering
from naoqi import ALProxy, ALBroker  # NAOqi-proxies og broker

# --------------------------------------------------------------------------------
# Konfiguration af robotens IP og port
IP   = "192.168.1.155"
PORT = 9559

# Sti til velkomstbillede på robotens tablet
WELCOME_IMG_PATH = r"C:\Users\AZ38024\Pictures\Norma_Pictures\Norma_Welcome.png"

# Variabel til at holde styr på arm-kontrol
arm_mode = False
# Mål-vinkler for skuldre (til smooth styring)
left_target = 0.0
right_target = 0.0

# PS5-controller-mapping\axis_map = {
# Kommentar rettet:
# PS5-controller-mapping
axis_map = {
    "move_x": 0,
    "move_y": 1,
    "head_yaw": 2,
    "head_pitch": 3,
    "l2": 4,
    "r2": 5
}
button_map = {
    "cross": 0,
    "circle": 1,
    "square": 2,
    "triangle": 3,
    "create": 4,
    "options": 6,
    "l3": 7,
    "r3": 8,
    "l1": 9,
    "r1": 10,
    "dpad_up": 11,
    "dpad_down": 12,
    "dpad_left": 13,
    "dpad_right": 14
}

# Broker
broker = ALBroker("myBroker", "0.0.0.0", 0, IP, PORT)
# --------------------------------------------------------------------------------

def show_welcome_image(tablet, animation, image_path):
    """Sky-gestus og vis velkomstbillede på tablet."""
    animation.runTag("sky")
    time.sleep(0.5)
    try:
        data = open(image_path, "rb").read()
    except Exception as e:
        print("Kunne ikke læse billede: %s" % e)
        return
    b64 = base64.b64encode(data)
    html = (
        "<html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/></head>"
        "<body style=\"margin:0;display:flex;justify-content:center;align-items:center;height:100vh;background:#fff;\">"
        "<img src=\"data:image/png;base64,%s\" style=\"max-width:100%%;max-height:100%%;object-fit:contain;\"/></body></html>"
    ) % b64
    uri = "data:text/html;base64," + base64.b64encode(html)
    tablet.showWebview(uri)
    print("Åbner Norma Welcome billede...")

# --------------------------------------------------------------------------------

def get_camera_frame(video_proxy, video_client):
    """Hent billede fra kamera."""
    img = video_proxy.getImageRemote(video_client)
    if img:
        w, h = img[0], img[1]
        return np.fromstring(img[6], dtype=np.uint8).reshape((h, w, 3))
    return None

# --------------------------------------------------------------------------------

def detect_faces(frame, face_cascade):
    """Tegn rektangler om ansigter."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    return frame

# --------------------------------------------------------------------------------

def process_joystick_input(js, motion):
    """Styr bevægelse og hoved baseret på PS5-aksen."""
    pygame.event.pump()
    x = js.get_axis(axis_map["move_x"])
    y = -js.get_axis(axis_map["move_y"])
    yaw = js.get_axis(axis_map["head_yaw"])
    pitch = -js.get_axis(axis_map["head_pitch"])
    if abs(x) < 0.2: x = 0
    if abs(y) < 0.2: y = 0
    if abs(yaw) < 0.2: yaw = 0
    if abs(pitch) < 0.2: pitch = 0
    motion.move(y * 0.5, 0, x * 0.5)
    cy = motion.getAngles("HeadYaw", True)[0]
    cp = motion.getAngles("HeadPitch", True)[0]
    motion.setAngles([
        "HeadYaw", "HeadPitch"
    ], [
        np.clip(cy + yaw * 0.2, -2.0, 2.0),
        np.clip(cp + pitch * 0.2, -0.5, 0.5)
    ], 0.1)

# --------------------------------------------------------------------------------

def process_joystick_buttons(js, tts, animation, motion, dbg_screen, font):
    """Smooth arm control, korrekt TTS og vis knapstatus."""
    global arm_mode, left_target, right_target
    # Indsæt mappings lokalt
    a = axis_map
    b = button_map
    if js.get_button(b["options"]):
        arm_mode = not arm_mode
        if arm_mode:
            tts.say("Nu kan du styre mine arme")
        else:
            tts.say("nu styrer jeg selv mine arme")
        pygame.time.wait(300)
    if arm_mode:
        val_l2 = js.get_axis(a["l2"])
        val_r2 = js.get_axis(a["r2"])
        left_target += val_l2 * 0.02
        right_target += val_r2 * 0.02
        left_target = np.clip(left_target, -1.5, 1.5)
        right_target = np.clip(right_target, -1.5, 1.5)
        motion.setAngles([
            "LShoulderPitch", "RShoulderPitch"
        ], [left_target, right_target], 0.05)
    else:
        for name, tag in [
            ("cross", "enthusiastic"),
            ("circle", "crazy"),
            ("square", "enthusiastic"),
            ("triangle", "agitated")
        ]:
            if js.get_button(b[name]):
                animation.runTag(tag)
                tts.say({
                    "cross": "Hej, jeg hedder Norma",
                    "circle": "Prutbanan",
                    "square": "Firkant aktiv!",
                    "triangle": "Trekant aktiv!"
                }[name])
                pygame.time.wait(300)
    dbg_screen.fill((0, 0, 0))
    for idx, name in enumerate(["cross", "circle", "square", "triangle"]):
        color = (0, 255, 0) if js.get_button(b[name]) else (100, 100, 100)
        text = font.render(name, True, color)
        dbg_screen.blit(text, (10 + idx * 90, 10))
    pygame.display.flip()

# --------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        tts = ALProxy("ALTextToSpeech", IP, PORT)
        animation = ALProxy("ALAnimationPlayer", IP, PORT)
        tablet = ALProxy("ALTabletService", IP, PORT)
        video_proxy = ALProxy("ALVideoDevice", IP, PORT)
        motion = ALProxy("ALMotion", IP, PORT)
    except Exception as e:
        print("Fejl ved forbindelse: %s" % e)
        sys.exit(1)
    video_client = video_proxy.subscribeCamera("camera_top", 0, 1, 13, 10)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    pygame.init()
    pygame.joystick.init()
    pygame.font.init()
    if pygame.joystick.get_count() == 0:
        print("Ingen controller fundet!")
        sys.exit(1)
    js = pygame.joystick.Joystick(0)
    js.init()
    dbg_screen = pygame.display.set_mode((400, 50))
    pygame.display.set_caption("Knappress Debug")
    font = pygame.font.SysFont(None, 24)
    cv2.namedWindow("Norma Cam", cv2.WINDOW_AUTOSIZE)
    show_welcome_image(tablet, animation, WELCOME_IMG_PATH)
    try:
        while True:
            frame = get_camera_frame(video_proxy, video_client)
            if frame is not None:
                cv2.imshow("Norma Cam", detect_faces(frame, face_cascade))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            process_joystick_input(js, motion)
            process_joystick_buttons(js, tts, animation, motion, dbg_screen, font)
    except KeyboardInterrupt:
        print("Stopper...")
        motion.stopMove()
    finally:
        pygame.quit()
        cv2.destroyAllWindows()
        broker.shutdown()
