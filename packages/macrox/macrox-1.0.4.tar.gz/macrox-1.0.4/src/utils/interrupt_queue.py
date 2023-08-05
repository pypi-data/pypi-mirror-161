import threading
import globals
from utils import logger, debugger

class InterruptQueue():
    def __init__(self):
        self.stack = []
        self.threads = []
        self.running = False
        self.threads_running = False

        self.interrupt = False

    def add(self, label, interrupt_obj):
        label_obj = globals.JH.get(label)
        self.stack.append(label_obj)
        if not self.running:
            self.run_thread = threading.Thread(target=self.run, args=(interrupt_obj,))
            self.run_thread.setName('Interrupt Queue Thread')
            self.run_thread.start()


    def run(self, interrupt_obj):
        self.interrupt = True
        self.running = True
        while True:
            if len(self.stack) == 0:
                break
            label = self.stack[0]
            label.evaluate(jump=True, ignore_int=True)
            interrupt_obj.resume()
            self.stack.pop(0)
        self.running = False
        self.interrupt = False