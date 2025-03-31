from naoqi import ALProxy
import pygame
import time

# Connect to Norma
IP = "192.168.1.155"
PORT = 9559

# Mode flags to track if we are in arm control mode or quick move mode
arm_mode = False
quick_move_mode = False

# Initialize Pygame for UI
def init_ui():
    pygame.display.set_caption("Norma Control Mode")
    return pygame.display.set_mode((400, 200))

def update_ui(screen, battery_level, servo_status, quick_move_mode):
    screen.fill((0, 0, 0))  # Black background
    font = pygame.font.Font(None, 36)

    mode_text = "Mode: Arm Control" if arm_mode else "Mode: Normal"
    text_surface = font.render(mode_text, True, (255, 255, 255))
    screen.blit(text_surface, (50, 80))

    battery_text = "Battery: {}%".format(battery_level)
    battery_surface = font.render(battery_text, True, (255, 255, 255))
    screen.blit(battery_surface, (50, 120))

    servo_text = "Servos: {}".format("OK" if servo_status else "Error")
    servo_surface = font.render(servo_text, True, (255, 255, 255))
    screen.blit(servo_surface, (50, 160))

    quick_move_text = "Quick Move: {}".format("ON" if quick_move_mode else "OFF")
    quick_move_surface = font.render(quick_move_text, True, (255, 255, 255))
    screen.blit(quick_move_surface, (50, 40))

    pygame.display.flip()

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
    move_speed = 0.7 if quick_move_mode else 0.5  # Adjust speed of movement
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

    # Move Norma's body
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
    global arm_mode, quick_move_mode

    # Check if Start button is pressed to toggle arm mode
    if joystick.get_button(7):  # Start button
        arm_mode = not arm_mode
        if arm_mode:
            tts.say("Nu kan du styre mine arme")
        else:
            tts.say("Nu styrer jeg selv mine arme")
        pygame.time.wait(500)

    # Check if View button is pressed to toggle quick move mode
    if joystick.get_button(8):  # View button
        quick_move_mode = not quick_move_mode
        if quick_move_mode:
            tts.say("Quick move mode activated")
        else:
            tts.say("Quick move mode deactivated")
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
            animation.runTag("enthusiastic")
            tts.say("Hej, jeg hedder Norma")
            pygame.time.wait(2000)

        if joystick.get_button(1):  # B button
            animation.runTag("crazy")
            tts.say("Du har trykket B sa jeg laver en lille dans!")
            pygame.time.wait(2000)

        if joystick.get_button(2):  # X button
            animation.runTag("enthusiastic")
            tts.say("Du har trykket pa X, sa jeg er glad idag")
            pygame.time.wait(2000)

        if joystick.get_button(3):  # Y button
            animation.runTag("agitated")
            tts.say("Du har trykket pa Y, sa nu er jeg sur")
            pygame.time.wait(2000)

def initialize_proxies():
    try:
        tts = ALProxy("ALTextToSpeech", IP, PORT)
        motion = ALProxy("ALMotion", IP, PORT)
        animation = ALProxy("ALAnimationPlayer", IP, PORT)
        battery = ALProxy("ALBattery", IP, PORT)
        return tts, motion, animation, battery
    except Exception as e:
        print("Error initializing proxies: {}".format(e))
        return None, None, None, None

def initialize_joystick():
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("No controller detected! Please connect an Xbox One controller.")
        return None
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Connected to:", joystick.get_name())
    return joystick

def check_servo_status(motion):
    try:
        stiffness = motion.getStiffnesses("Body")
        return all(s > 0.5 for s in stiffness)
    except Exception as e:
        print("Error checking servo status: {}".format(e))
        return False

def get_battery_level(battery):
    try:
        return battery.getBatteryCharge()
    except Exception as e:
        print("Error getting battery level: {}".format(e))
        return 0

def main():
    tts, motion, animation, battery = initialize_proxies()
    if not tts or not motion or not animation or not battery:
        return

    screen = init_ui()
    joystick = initialize_joystick()
    if not joystick:
        return

    try:
        animation.runTag("cloud")
        tts.say("Jeg virker")
        print("Starting movement control...")

        while True:
            process_joystick_input(joystick, motion)
            process_joystick_buttons(joystick, tts, animation, motion)

            # Update diagnostics
            battery_level = get_battery_level(battery)
            servo_status = check_servo_status(motion)

            update_ui(screen, battery_level, servo_status, quick_move_mode)
            time.sleep(0.1)  # Add a small delay to reduce CPU usage
    except KeyboardInterrupt:
        print("Stopping Pepper movement...")
        motion.stopMove()
        pygame.quit()
        return

main()
