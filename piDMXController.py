## Raspberry Pi controller for ENTTEC DMX USB PRO Mk2 & DMX hardware

# Import PySerial from pip install path & assign ENTTEC PRO port to ser variable
import sys
sys.path.append('/home/pi/.local/lib/python2.7/site-packages')
import serial

# Initialize DmxPy on port connecting ENTTEC DMX USB PRO to RPi
from DmxPy import DmxPy
dmx = DmxPy('/dev/ttyUSB0')

# Import RPi GPIO pin controllers
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
  btn_red_state = GPIO.input(18)
  btn_yel_state = GPIO.input(17)
  btn_grn_state = GPIO.input(27)
  if btn_red_state == False:
    print('Red button pressed')
    playConversation(0)
    time.sleep(1)
  elif btn_yel_state == False:
    print('Yellow button pressed')
    playConversation(1)
    time.sleep(1)
  elif btn_grn_state == False:
    print('Green button pressed')
    playConversation(2)
    time.sleep(1)


