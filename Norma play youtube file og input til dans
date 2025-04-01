from naoqi import ALProxy
import pygame
import time

# Set up the connection details for Pepper
IP = "192.168.1.155"
PORT = 9559

# Initialize pygame and the joystick (Xbox controller)
pygame.init()
pygame.joystick.init()

# Initialize text-to-speech and animation proxies
tts = ALProxy("ALTextToSpeech", IP, PORT)
animation = ALProxy("ALAnimationPlayer", IP, PORT)
tablet_service = ALProxy("ALTabletService", IP, PORT)

# Play YouTube video
def play_video():
    try:
        tablet_service.showWebview()  # Show the webview
        tablet_service.loadUrl("https://www.youtube.com/watch?v=kuG3uTCb5a4")  # URL of the video
        print("Video is now playing.")
    except Exception as e:
        print("Error in video playback:", e)

# Perform the dance cycle with gestures
def perform_dance_cycle(joystick):
    gestures = ["crazy", "exalted", "happy", "hello"]
    current_gesture = 0  # Start from the first gesture

    while True:
        pygame.event.pump()
        
        # Detect if A button is pressed
        if joystick.get_button(0):  # A button
            print("Performing gesture:", gestures[current_gesture])
            animation.runTag(gestures[current_gesture])  # Perform the gesture
            tts.say("Now performing " + gestures[current_gesture] + " gesture")

            # Wait for the animation to finish before moving to the next gesture
            pygame.time.wait(2000)  # Adjust timing based on the length of gestures

            # Move to the next gesture in the cycle
            current_gesture = (current_gesture + 1) % len(gestures)

            # Optionally, you can also play some music or add effects here if needed.
            time.sleep(0.5)  # Small delay between gestures to simulate fluid dancing

def main():
    # Check if an Xbox controller is connected
    if pygame.joystick.get_count() == 0:
        print("No controller detected! Please connect an Xbox One controller.")
        return
    
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Connected to:", joystick.get_name())
    
    # Start video playback in the background
    play_video()

    # Start performing the dance cycle
    perform_dance_cycle(joystick)

# Run the main loop
main()
