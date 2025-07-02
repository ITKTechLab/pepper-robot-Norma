from naoqi import ALProxy
import pygame
import cv2
import numpy as np

# Connect to Norma (SoftBank Pepper Robot)
IP = "192.168.1.155"
PORT = 9559

# Mode flag to track if we are in arm control mode
arm_mode = False

# Initialize video streaming from Pepper's camera
video_proxy = ALProxy("ALVideoDevice", IP, PORT)
resolution = 1  # 160x120 resolution for low quality
color_space = 13  # BGR color space (compatible with OpenCV)
fps = 10  # Lower FPS to reduce network and processing load

# Subscribe to the top camera feed
camera_name = "camera_top"
video_client = video_proxy.subscribeCamera(camera_name, 0, resolution, color_space, fps)

# Load OpenCV's Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Disable full-body tracking but keep head tracking active
motion = ALProxy("ALMotion", IP, PORT)
motion.setStiffnesses("Head", 1.0)  # Keep head stiff for controlled movement
motion.wbEnable(False)  # Disable whole-body tracking

def get_camera_frame():
    """Fetches a frame from Pepper's camera and converts it to a NumPy array."""
    image_container = video_proxy.getImageRemote(video_client)
    if image_container:
        width, height = image_container[0], image_container[1]
        array = np.fromstring(image_container[6], dtype=np.uint8).reshape((height, width, 3))
        return array
    return None

def detect_faces(frame):
    """Detects faces in the given frame and draws green rectangles around them."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale for detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return frame

def process_joystick_input(joystick, motion):
    """Processes joystick inputs for Pepper's movement and head control."""
    pygame.event.pump()  # Update pygame event queue
    
    # Read joystick axis values
    x_axis = joystick.get_axis(0)  # Left joystick X-axis for rotation
    y_axis = -joystick.get_axis(1)  # Left joystick Y-axis for forward/backward movement
    head_yaw = joystick.get_axis(2)  # Right joystick X-axis for head yaw
    head_pitch = -joystick.get_axis(3)  # Right joystick Y-axis for head pitch
    
    # Define movement thresholds
    threshold = 0.2
    move_speed = 0.5  # Movement speed scale
    head_speed = 0.2  # Head movement speed scale

    # Apply dead zones (ignore small joystick movements)
    if abs(x_axis) < threshold:
        x_axis = 0
    if abs(y_axis) < threshold:
        y_axis = 0
    if abs(head_yaw) < threshold:
        head_yaw = 0
    if abs(head_pitch) < threshold:
        head_pitch = 0

    # Move Pepper based on joystick input
    motion.move(y_axis * move_speed, 0, x_axis * move_speed)
    
    # Get current head angles
    current_yaw = motion.getAngles("HeadYaw", True)[0]
    current_pitch = motion.getAngles("HeadPitch", True)[0]
    
    # Apply limits to head movement
    new_yaw = max(-2.0, min(2.0, current_yaw + head_yaw * head_speed))
    new_pitch = max(-0.5, min(0.5, current_pitch + head_pitch * head_speed))
    
    # Set new head angles
    motion.setAngles(["HeadYaw", "HeadPitch"], [new_yaw, new_pitch], 0.1)

def process_joystick_buttons(joystick, tts, animation, motion):
    """Handles button inputs for animations, speech, and arm control."""
    global arm_mode
    
    # Toggle arm control mode
    if joystick.get_button(7):  # Start button
        arm_mode = not arm_mode
        tts.say("Nu kan du styre mine arme" if arm_mode else "Nu styrer jeg selv mine arme")
        pygame.time.wait(500)  # Prevent repeated toggling
    
    if arm_mode:
        # Arm control using triggers and bumpers
        left_shoulder = "LShoulderPitch"
        right_shoulder = "RShoulderPitch"
        current_left = motion.getAngles(left_shoulder, True)[0]
        current_right = motion.getAngles(right_shoulder, True)[0]
        shoulder_step = 0.05
        trigger_sensitivity = 0.1

        if joystick.get_button(4):  # Left bumper
            motion.setAngles(left_shoulder, max(-1.5, current_left - shoulder_step), 0.05)
        if joystick.get_button(5):  # Right bumper
            motion.setAngles(right_shoulder, max(-1.5, current_right - shoulder_step), 0.05)

        lt_value = joystick.get_axis(4)  # Left trigger
        if lt_value > 0.1:
            motion.setAngles(left_shoulder, min(1.5, current_left + lt_value * trigger_sensitivity), 0.05)

        rt_value = joystick.get_axis(5)  # Right trigger
        if rt_value > 0.1:
            motion.setAngles(right_shoulder, min(1.5, current_right + rt_value * trigger_sensitivity), 0.05)
    else:
        # Button-mapped gestures and speech
        if joystick.get_button(0):  # A button
            animation.runTag("enthusiastic")
            tts.say("Hej, jeg hedder Norma")
        if joystick.get_button(1):  # B button
            animation.runTag("crazy")
            tts.say("Du har trykket B sa jeg laver en lille dans!")
        if joystick.get_button(2):  # X button
            animation.runTag("enthusiastic")
            tts.say("Du har trykket pa kryds, sa jeg er glad idag")
        if joystick.get_button(3):  # Y button
            animation.runTag("agitated")
            tts.say("Du har trykket pa Y, sa nu er jeg sur")

def main():
    """Main function to initialize and run the Xbox-controlled Pepper system."""
    try:
        tts = ALProxy("ALTextToSpeech", IP, PORT)
        motion = ALProxy("ALMotion", IP, PORT)
        animation = ALProxy("ALAnimationPlayer", IP, PORT)
        animation.runTag("cloud")
        tts.say("Jeg virker")
    except Exception as e:
        print("Error connecting to Norma: {}".format(e))
        return

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller detected! Please connect an Xbox One controller.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    cv2.namedWindow("Norma Camera", cv2.WINDOW_AUTOSIZE)
    
    while True:
        frame = get_camera_frame()
        if frame is not None:
            cv2.imshow("Norma Camera", detect_faces(frame))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        process_joystick_input(joystick, motion)
        process_joystick_buttons(joystick, tts, animation, motion)
    
    motion.stopMove()
    pygame.quit()
    cv2.destroyAllWindows()

main()
