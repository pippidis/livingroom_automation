import time
import RPi.GPIO as GPIO
from datetime import datetime
import pytz
import sys
import os
import vlc

# Defining plans
light_plan = [
    {'on':{'hr':8, 'min':0}, 'off':{'hr':20, 'min':0}}
]

pump_plan = [
    {'on':{'hr':7, 'min':0}, 'off':{'hr':8, 'min':0}}
]

# Defining pins (# = confirmend)
LIGHT_RELE_PLANT_WALL = 11 #
LIGHT_TOGLE_ON =  19 #
LIGHT_TOGLE_OFF = 21 #
LIGHT_PAUSE = 23 #

PUMP_RELE_LEFT = 13 #
PUMP_RELE_RIGHT = 15 #
PUMP_TOGLE_ON = 33 #
PUMP_TOGLE_OFF = 37 #
PUMP_PAUSE = 36 #

FAN_ON = 40 #
FAN_OFF = 38 #
FAN_RELE = 16 #

TEMP_DATA = 32 
RED_SWITCH = 31 #

# Some standard variables
PAUSE_DURATION = 7200 # secounds
PAUSE_LATCH = 3 # secounds - How long before it can be reset

# Setting up the board
print(__file__,'Setting up GPIO')
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LIGHT_RELE_PLANT_WALL, GPIO.OUT)
GPIO.setup(LIGHT_TOGLE_ON, GPIO.IN)
GPIO.setup(LIGHT_TOGLE_OFF, GPIO.IN)
GPIO.setup(LIGHT_PAUSE, GPIO.IN)

GPIO.setup(PUMP_RELE_LEFT, GPIO.OUT)
GPIO.setup(PUMP_RELE_RIGHT, GPIO.OUT)
GPIO.setup(PUMP_TOGLE_ON, GPIO.IN)
GPIO.setup(PUMP_TOGLE_OFF, GPIO.IN)
GPIO.setup(PUMP_PAUSE, GPIO.IN)

GPIO.setup(FAN_ON, GPIO.IN)
GPIO.setup(FAN_OFF, GPIO.IN)

GPIO.setup(TEMP_DATA, GPIO.IN)
GPIO.setup(RED_SWITCH, GPIO.IN)
GPIO.setup(FAN_RELE, GPIO.OUT)


def is_paused(status:float=0, pressed:bool=False, when=None, duration:float=PAUSE_DURATION, latch:float=PAUSE_LATCH)-> tuple[float, bool]:
    '''Return of it is paused or not'''
    if not when: when = time.time() # sets the current time as when
    # Getting a couple of logical situations
    time_from_status = abs(when) - abs(status) 
    status_is_positive = status > 0
    status_is_negative = status < 0
    status_is_null = status == 0
     
    # If in latch: 
    if time_from_status < PAUSE_LATCH:
        if status_is_positive: return status, True
        if status_is_negative: return status, False
        if status_is_null: return status, False

    # If the button is pressed: 
    if pressed: 
        if status_is_positive: return -when, False
        if status_is_negative: return when, True
        if status_is_null: return when, True
    
    # If over time: 
    if time_from_status > duration: 
        if status_is_positive: return 0, False 

    # If it is in pause, but not over time: 
    if status_is_positive: 
        return status, True

    # Fallback
    return status, False

def state_from_plan(plan, when:float=None) -> bool:
    tz_OSLO = pytz.timezone('Europe/Oslo') 
    if not when: when = datetime.now(tz_OSLO)
    '''returns the desired state the given plant now'''
    for period in plan: 
        on = when.replace(hour=period['on']['hr'], minute=period['on']['min'])
        off = when.replace(hour=period['off']['hr'], minute=period['off']['min'])
        if when <= off and when >= on:
            return True
    return False

def alternate_pumps(period:int=5) -> str:
    '''Alternate the two pumps based on the time'''
    minutes = time.time() / 60 # Get the number of minutes since the beginning of time
    time_left = minutes % period*2
    half_period = period
    if time_left >= half_period: return 'left'
    return 'right'
    
def control_light(plan, pause_status) -> float:
    '''Logic to controll the light'''
    if GPIO.input(LIGHT_TOGLE_OFF) is GPIO.LOW: 
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.LOW)
        return pause_status

    # Pause logic:
    pause_status, paused = is_paused(status=pause_status, pressed=GPIO.input(LIGHT_PAUSE) is GPIO.LOW)
    if paused:
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.LOW)
        return pause_status

    # The togle: 
    if GPIO.input(LIGHT_TOGLE_ON) is GPIO.LOW: 
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.HIGH)
        return pause_status
    
    # The plan
    if state_from_plan(plan):
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.HIGH)
        return pause_status
    
    # Off is not on
    GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.LOW)
    return pause_status

def control_pumps(plan, pause_status) -> float:
    '''Controll the pumps'''
    if GPIO.input(PUMP_TOGLE_OFF) is GPIO.LOW: 
        GPIO.output(PUMP_RELE_LEFT, GPIO.LOW)
        GPIO.output(PUMP_RELE_RIGHT, GPIO.LOW)
        return pause_status

    pause_status, paused = is_paused(status=pause_status, pressed=GPIO.input(PUMP_PAUSE) is GPIO.LOW)
    if paused:
        GPIO.output(PUMP_RELE_LEFT, GPIO.LOW)
        GPIO.output(PUMP_RELE_RIGHT, GPIO.LOW)
        return pause_status

    if GPIO.input(PUMP_TOGLE_ON) is GPIO.LOW: 
        GPIO.output(PUMP_RELE_LEFT, GPIO.HIGH)
        GPIO.output(PUMP_RELE_RIGHT, GPIO.HIGH)
        return pause_status

    if state_from_plan(plan):
        pump_to_run = alternate_pumps()
        if pump_to_run == 'left':
            GPIO.output(PUMP_RELE_LEFT, GPIO.HIGH)
            GPIO.output(PUMP_RELE_RIGHT, GPIO.LOW)
        if pump_to_run == 'right': 
            GPIO.output(PUMP_RELE_LEFT, GPIO.LOW)
            GPIO.output(PUMP_RELE_RIGHT, GPIO.HIGH)
        return pause_status
    
    # Off if not on
    GPIO.output(PUMP_RELE_LEFT, GPIO.LOW)
    GPIO.output(PUMP_RELE_RIGHT, GPIO.LOW)
    return pause_status

def control_fan() -> None:
    '''Controlls the fan'''
    if GPIO.input(FAN_ON) is GPIO.LOW: 
        GPIO.output(FAN_RELE, GPIO.HIGH)
    else: 
        GPIO.output(FAN_RELE, GPIO.LOW)

def update() -> None:
    '''Updates the rasberry pi if certian conditions are met'''
    fan_toggle: bool = GPIO.input(FAN_OFF) is GPIO.LOW
    pump_toggle: bool = GPIO.input(PUMP_TOGLE_OFF) is GPIO.LOW
    light_toggle: bool = GPIO.input(LIGHT_TOGLE_OFF) is GPIO.LOW
    red_button: bool = GPIO.input(RED_SWITCH) is GPIO.LOW
    if fan_toggle and pump_toggle and light_toggle and red_button: 
        os.system('bash tvpi_startup.sh &') # Starts the startup bash. The scripts waits for 1s before beginning
        sys.exit("### Pulling new code from github ###") # exits the program

def video_setup(source) -> tuple[vlc.Instance, list]:
    # Setting up the vlc instance
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
     
    # creating a media
    media = vlc_instance.media_new(source)
     
    # setting media to the player
    player.set_media(media)

def video_control(media_player) -> None:
    is_playing = media_player.is_playing()
    print(is_playing)



def main(light_plan, pump_plan, testing=False) -> None:
    '''The main function, runs the whole thing'''
    light_pause_status:float = 0
    pump_pause_status:float = 0
    media_player = video_setup('test_video.mp4')
    print(__file__,'Entering main loop')
    while True:
        update() # If the system should be updated
        video_control(media_player)
        light_pause_status = control_light(plan=light_plan, pause_status=light_pause_status)
        pump_pause_status = control_pumps(plan=pump_plan, pause_status=pump_pause_status)

        control_fan()

        if testing:
            print('-'*60)
            print(__file__, 'LIGHT_TOGLE_ON', LIGHT_TOGLE_ON, GPIO.input(LIGHT_TOGLE_ON))
            print(__file__, 'LIGHT_TOGLE_OFF', LIGHT_TOGLE_OFF, GPIO.input(LIGHT_TOGLE_OFF))
            print(__file__, 'LIGHT_PAUSE', LIGHT_PAUSE, GPIO.input(LIGHT_PAUSE))
            print(__file__, 'PUMP_TOGLE_ON', PUMP_TOGLE_ON, GPIO.input(PUMP_TOGLE_ON))
            print(__file__, 'PUMP_TOGLE_OFF', PUMP_TOGLE_OFF, GPIO.input(PUMP_TOGLE_OFF))
            print(__file__, 'PUMP_PAUSE', PUMP_PAUSE, GPIO.input(PUMP_PAUSE))
            print(__file__, 'FAN_ON', FAN_ON, GPIO.input(FAN_ON))
            print(__file__, 'FAN_OFF', FAN_OFF, GPIO.input(FAN_OFF))
            print(__file__, 'TEMP_DATA', TEMP_DATA, GPIO.input(TEMP_DATA))
            print(__file__, 'RED_SWITCH', RED_SWITCH,  GPIO.input(RED_SWITCH))

            time.sleep(1) #reduces the speed
        time.sleep(0.05) # To reduce load
        
if __name__ == '__main__': 
    try: 
        video('test_video.mp4')
        main(light_plan, pump_plan, testing=False)
    except Exception as e:
        print(__file__,'Something went wrong in the main loop', e) 
    finally:
        GPIO.cleanup()