import mouse
import keyboard
import pickle
from utils import logger

class Recorder():
    def __init__(self) -> None:
        self.mouse_events = []
        self.keyboard_events = []
        
    def record(self, key, actionfile):
        logger.info('Recording started!')
        mouse.hook(self.mouse_events.append)
        keyboard.start_recording()

        keyboard.wait(key)

        logger.info('Recording stopped!')

        mouse.unhook(self.mouse_events.append)
        self.keyboard_events = keyboard.stop_recording()

        self.save(actionfile)
    
    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump({
                'mouse': self.mouse_events,
                'keyboard': self.keyboard_events
            }, file)
            file.close
    
    def wait_for(self, key, actionfile):
        logger.info('Started recorder listener!')
        logger.info(f'Press {key} to start the recording and press it another time to stop the recording!')

        keyboard.wait(key)
        self.record(key, actionfile)