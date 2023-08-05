from nodes import bases
from time import sleep
from utils import logger

class SleepNode(bases.InstructionNode):
    KIND = 'SleepNode'
    def __init__(self, time: int) -> None:
        self.time = time

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        ms = self.time
        if not isinstance(ms, int):
            logger.error('Invalid millisecond value!', command='sleep')
        
        sleep(ms / 1000)

    def prettyprint(self, indent):
        indent_str = ' '*indent
        return f'{self.KIND} (\n{indent_str}    Time: {str(self.time)}ms\n{indent_str})'