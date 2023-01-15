import time
import RPi.GPIO as GPIO
from datetime import datetime

# Defining plans
light_plan = [
    {'on':{'hr':8, 'min':0}, 'off':{'hr':20, 'min':0}}
]

pump_plan = [
    {'on':{'hr':7, 'min':0}, 'off':{'hr':8, 'min':0}}
]

# Defining pins
LIGHT_RELE_PLANT_WALL = 12
LIGHT_TOGLE_ON = 7
LIGHT_TOGLE_OFF = 11
LIGHT_PAUSE = 13

PUMP_RELE_LEFT = 16
PUMP_RELE_RIGHT = 18
PUMP_TOGLE_ON = 15
PUMP_TOGLE_OFF = 19
PUMP_PAUSE = 21 

RELE_4 = 22 # Not in use

# Setting up the board
print('automation.py','Setting up GPIO')
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


# Some standard variables
PAUSE_DURATION = 7200 # secounds
PAUSE_RESET_WAIT = 2 # secounds - How long before it can be reset


def is_paused(chanel, pause_start:float=0.0, pause_duration:float=PAUSE_DURATION, pause_reset_wait:float=PAUSE_RESET_WAIT) -> tuple[bool, float]:
    '''Return if the thing is paused or not'''
    chanel_is_pressed = GPIO.input(chanel) is GPIO.HIGH
    in_pause = pause_start > 0
    in_reset_wait_time = 0 < time.time() - pause_start < pause_reset_wait

    # It is not in pause, and the button is pressed
    if chanel_is_pressed and not in_pause: 
        return True, time.time()
    
    # It is in pause, not in the reset wait time, and the button is presset - reset
    if chanel_is_pressed and in_pause and not in_reset_wait_time:
        return False, float(-1)
    
    # Time is over
    if in_pause and time.time() - pause_duration > pause_start:
        return False, float(-1)

    # It is in pause
    return True, pause_start

def state_from_plan(plan, when:float=datetime.now()) -> bool:
    '''returns the desired state the given plant now'''
    for period in plan: 
        on = when.replace(hour=period['on']['hr'], minute=period['on']['min'])
        off = when.replace(hour=period['off']['hr'], minute=period['off']['min'])
        if when <= off and when >= on:
            return True
    return False

def control_light(light_plan, pause_start) -> float:
    '''Logic to controll the light'''
    # Pause logic:
    paused, pause_start = is_paused(LIGHT_PAUSE, pause_start)
    if paused:
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.LOW)
        return pause_start

    # The togle: 
    togle_on_state = GPIO.input(LIGHT_TOGLE_ON) is GPIO.LOW
    togle_off_state = GPIO.input(LIGHT_TOGLE_OFF) is GPIO.LOW
    if togle_on_state: 
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.HIGH)
        return pause_start
    if togle_off_state: 
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.LOW)
        return pause_start

    # The plan
    if state_from_plan(light_plan):
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.HIGH)
        return pause_start
    
    # Off is not on
    GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.LOW)
    return pause_start

def main(light_plan, pump_plan, testing=False) -> None:
    '''The main function, runs the whole thing'''
    light_pause_start:float = -1
    print('automation.py','Entering main loop')
    while True:
        if testing:
            print('automation.py','-'*50)
            print('automation.py','LIGHT_TOGLE_ON', GPIO.input(LIGHT_TOGLE_ON))
            print('automation.py','LIGHT_TOGLE_ON', GPIO.input(LIGHT_TOGLE_OFF))
            print('automation.py','LIGHT_TOGLE_ON', GPIO.input(LIGHT_PAUSE))

        light_pause_start = control_light(light_plan, pause_start=light_pause_start)
    
        print('This is probably a test')
        time.sleep(0.05) # To reduce load
        if testing: time.sleep(1) #reduces the speed


if __name__ == '__main__': 
    try: 
        main(light_plan, pump_plan, testing=True)
    except Exception as e:
        print('Something went wrong in the main loop', e) 
    finally:
        GPIO.cleanup()