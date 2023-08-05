from nodes import bases
from utils import logger
import pickle
import mouse
import keyboard
import threading
import os

class ReplayNode(bases.InstructionNode):
    KIND = 'ReplayNode'
    def __init__(self, action_name) -> None:
        self.action_name = action_name

        self.mouse_events = []
        self.keyboard_events = []

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        if not os.path.exists(self.action_name):
            logger.error(f'Actionfile "{self.action_name}" does not exist!')
        
        self.load(self.action_name)
        self.replay()

        
    def load(self, filename):
        with open(f'{filename}.mof', 'rb') as file:
            dict_ = pickle.load(file)
            file.close()
        
        self.mouse_events = dict_['mouse']
        self.keyboard_events = dict_['keyboard']
    
    
    def replay(self):
        k_thread = threading.Thread(target = lambda: keyboard.play(self.keyboard_events))
        k_thread.start()

        m_thread = threading.Thread(target = lambda: mouse.play(self.mouse_events))
        m_thread.start()

        #waiting for both threadings to be completed

        k_thread.join() 
        m_thread.join()