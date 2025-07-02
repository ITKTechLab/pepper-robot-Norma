# Hent alle de biblioteker som Norma har brug for 
from naoqi import ALProxy
import pygame

# Connect to Norma
IP = "192.168.1.155"
PORT = 9559

# Mode flag to track if we are in arm control mode
arm_mode = False

# Function to map joystick input to Norma movement
def process_joystick_input(joystick, motion):
    pygame.event.pump()
    
    # Left joystick - Move Norma
    x_axis = joystick.get_axis(0)  # Left stick X-axis (-1 to 1, left to right)
    y_axis = -joystick.get_axis(1)  # Left stick Y-axis (-1 to 1, forward to backward)

    # Right joystick - Control head
    head_yaw = joystick.get_axis(2)  # Right stick X-axis (turn head left/right)
    head_pitch = -joystick.get_axis(3)  # Right stick Y-axis (look up/down)

    # Threshold to prevent unwanted small movements
    threshold = 0.2
    move_speed = 0.5  # Adjust speed of movement
    head_speed = 0.2  # Adjust speed of head movement

    # Ignore small joystick movements
    if abs(x_axis) < threshold:
        x_axis = 0
    if abs(y_axis) < threshold:
        y_axis = 0
    if abs(head_yaw) < threshold:
        head_yaw = 0
    if abs(head_pitch) < threshold:
        head_pitch = 0

    # Move Normas body
    motion.move(y_axis * move_speed, 0, x_axis * move_speed)

    # Get current head position
    current_yaw = motion.getAngles("HeadYaw", True)[0]
    current_pitch = motion.getAngles("HeadPitch", True)[0]

    # Calculate new head positions with limits
    new_yaw = current_yaw + head_yaw * head_speed
    new_pitch = current_pitch + head_pitch * head_speed

    # Limit head movement range
    new_yaw = max(-2.0, min(2.0, new_yaw))  # HeadYaw range (-2.0 to 2.0)
    new_pitch = max(-0.5, min(0.5, new_pitch))  # HeadPitch range (-0.5 to 0.5)

    # Move Norma's head
    motion.setAngles(["HeadYaw", "HeadPitch"], [new_yaw, new_pitch], 0.1)

def process_joystick_buttons(joystick, tts, animation, motion):
    global arm_mode
    
    # Check if Start button is pressed to toggle arm mode
    if joystick.get_button(7):  # Start button
        arm_mode = not arm_mode
        if arm_mode:
            tts.say("Nu kan du styre mine arme")
        else:
            tts.say("Nu styrer jeg selv mine arme")
        pygame.time.wait(500)
    
    if arm_mode:
        # Control arms with back buttons
        left_shoulder = "LShoulderPitch"
        right_shoulder = "RShoulderPitch"

        current_left = motion.getAngles(left_shoulder, True)[0]
        current_right = motion.getAngles(right_shoulder, True)[0]

        shoulder_step = 0.1

        if joystick.get_button(4):  # LB - Left arm up
            motion.setAngles(left_shoulder, max(-1.5, current_left - shoulder_step), 0.1)
        if joystick.get_button(5):  # RB - Right arm up
            motion.setAngles(right_shoulder, max(-1.5, current_right - shoulder_step), 0.1)
        if joystick.get_button(6):  # LT - Left arm down
            motion.setAngles(left_shoulder, min(1.5, current_left + shoulder_step), 0.1)
        if joystick.get_button(7):  # RT - Right arm down
            motion.setAngles(right_shoulder, min(1.5, current_right + shoulder_step), 0.1)
    else:
        # Normal button controls
        if joystick.get_button(0):  # A button
            print("A button pressed - Performing 'enthusiastic' gesture and saying 'Hej, jeg hedder Norma'.")
            animation.runTag("enthusiastic")
            tts.say("Hej, jeg hedder Norma")
            pygame.time.wait(2000)
        
        if joystick.get_button(1):  # B button
            print("B button pressed - Performing 'crazy' gesture and saying 'Du har trykket B sa jeg laver en lille dans!'.")
            animation.runTag("crazy")
            tts.say("Du har trykket B sa jeg laver en lille dans!")
            pygame.time.wait(2000)
        
        if joystick.get_button(2):  # X button
            print("X button pressed - Performing 'enthusiastic' gesture and saying 'Du har trykket pa X, sa jeg er glad idag'.")
            animation.runTag("enthusiastic")
            tts.say("Du har trykket pa X, sa jeg er glad idag")
            pygame.time.wait(2000)
        
        if joystick.get_button(3):  # Y button
            print("Y button pressed - Performing 'agitated' gesture and saying 'Du har trykket pa Y, sa nu er jeg sur'.")
            animation.runTag("agitated")
            tts.say("Du har trykket pa Y, sa nu er jeg sur")
            pygame.time.wait(2000)

def main():
    try:
        # Initialize text-to-speech proxy
        tts = ALProxy("ALTextToSpeech", IP, PORT)
        
        # Initialize motion proxy
        motion = ALProxy("ALMotion", IP, PORT)
        
        # Perform the "cloud" gesture at startup
        animation = ALProxy("ALAnimationPlayer", IP, PORT)
        animation.runTag("cloud")
        
        # Make Pepper say "Jeg virker"
        tts.say("Jeg virker")
        
        print("Starting movement control...")

    except Exception as e:
        print("Error connecting to Norma: {}".format(e))
        return

    # Initialize pygame and joystick
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller detected! Please connect an Xbox One controller.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Connected to:", joystick.get_name())

    try:
        while True:
            process_joystick_input(joystick, motion)
            process_joystick_buttons(joystick, tts, animation, motion)
    except KeyboardInterrupt:
        print("Stopping Pepper movement...")
        motion.stopMove()
        pygame.quit()
        return

main()
