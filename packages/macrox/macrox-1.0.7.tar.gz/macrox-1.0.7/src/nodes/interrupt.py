import time
from nodes import bases
from tokens import base_token
from utils import logger
import globals
import threading

class InterruptNode(bases.InstructionNode):
    KIND = 'InterruptNode'
    def __init__(self, label, condition) -> None:
        self.label = label[1:] #! Since first char is "~"!
        self.condition = condition


        self.thread = None
        self.kill = False
        self.wait = False
        
    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        if self.thread is None:
            logger.info('Starting condition checker thread...')
            self.thread = threading.Thread(target=self.check_condition)
            self.thread.setName('Interrupt Condition thread')
            self.thread.start()

    def check_condition(self):
        while not self.kill:
            if isinstance(self.condition, bases.Node):
                value = self.condition.evaluate(ignore_int=True)
            elif isinstance(self.condition, base_token.Token):
                if self.condition.token == 'Identifier':
                    value = globals.VH.get(self.condition.part)
                elif self.condition.token == 'LabelName':
                    value = globals.JH.jump(self.condition.part[1:], True)
                elif self.condition.token == 'Boolean':
                    value = self.condition
            else:
                logger.error(f'Condition type was not recognized. The condition was: {self.condition}')
            
            if value is True:
                

                globals.IQ.add(self.label, self)

                
               
                self.wait = True

            while self.wait:
                time.sleep(0.0000000000000000000000000000001)
    
    def resume(self):
        self.wait = False
    
    def pause(self):
        self.wait = True