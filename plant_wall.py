import yaml
from yaml.loader import SafeLoader
import time

# Importing the plan

def import_settings() -> dict:
    '''Import the settings from the file'''
    with open('plant_wall.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)
        print(data)
    return data


def main(settings) -> None:
    '''The main function, runns the whole thing'''
    while True:
        print('This is probably a stest')
        time.sleep(1)


if __name__ == '__main__': 
    settings = import_settings()
