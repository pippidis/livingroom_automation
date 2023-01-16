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
PAUSE_LATCH = 2 # secounds - How long before it can be reset

def paused(status:float=0, pressed:bool=False, when:time=time.time(), duration:float=PAUSE_DURATION, latch:float=PAUSE_LATCH)-> tuple[float, bool]:
    '''Return of it is paused or not'''
    print(__file__, ':', 'paused : status ', status, ': pressed ', pressed)
    # Getting a couple of logical situations
    time_from_status = when - abs(status) 
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

    # Fallback
    return status, False


def state_from_plan(plan, when:float=datetime.now()) -> bool:
    '''returns the desired state the given plant now'''
    for period in plan: 
        on = when.replace(hour=period['on']['hr'], minute=period['on']['min'])
        off = when.replace(hour=period['off']['hr'], minute=period['off']['min'])
        if when <= off and when >= on:
            return True
    return False

def control_light(light_plan, light_pause_status) -> float:
    '''Logic to controll the light'''
    # Pause logic:
    light_pause_button_pressed = GPIO.input(LIGHT_PAUSE) is GPIO.LOW
    light_pause_status, light_paused = paused(light_pause_status, light_pause_button_pressed)
    print('automation.py','paused, pause_start', light_paused, light_pause_status)
    if light_paused:
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.LOW)
        return light_pause_status

    # The togle: 
    togle_on_state = GPIO.input(LIGHT_TOGLE_ON) is GPIO.LOW
    togle_off_state = GPIO.input(LIGHT_TOGLE_OFF) is GPIO.LOW
    if togle_on_state: 
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.HIGH)
        return light_pause_status
    if togle_off_state: 
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.LOW)
        return light_pause_status

    # The plan
    if state_from_plan(light_plan):
        GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.HIGH)
        return light_pause_status
    
    # Off is not on
    GPIO.output(LIGHT_RELE_PLANT_WALL, GPIO.LOW)
    return light_pause_status

def main(light_plan, pump_plan, testing=False) -> None:
    '''The main function, runs the whole thing'''
    light_pause_start:float = -1
    print('automation.py','Entering main loop')
    while True:
        if testing:
            print('automation.py','-'*50)
            print('automation.py','LIGHT_TOGLE_ON', GPIO.input(LIGHT_TOGLE_ON))
            print('automation.py','LIGHT_TOGLE_OFF', GPIO.input(LIGHT_TOGLE_OFF))
            print('automation.py','LIGHT_PAUSE', GPIO.input(LIGHT_PAUSE))
            print('automation.py','light_pause_start', light_pause_start)

        light_pause_start = control_light(light_plan, light_pause_start)
    
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