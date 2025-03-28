import RPi.GPIO as GPIO
import time
import os

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)  # Assuming you are using GPIO17 for the button

while True:
    if GPIO.input(17) == GPIO.LOW:  # Button pressed
        # Shutdown
        #os.system("sudo shutdown -h now")
        # Reboot
        os.system("sudo reboot")
        time.sleep(0.2) # Debounce
