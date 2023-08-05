from utils import logger
from nodes import bases
from tokens import base_token

class JumpHandler():
    def __init__(self) -> None:
        self.jumps = {}

    def setup_jump(self, label, node):
        self.jumps[label[1:-1]] = node

    def jump(self, label, ignore_int):
        if label in self.jumps.keys():
            ret_val = self.jumps[label].evaluate(jump=True, ignore_int=ignore_int)
            if isinstance(ret_val, base_token.Token):
                return ret_val
            elif isinstance(ret_val, bases.Node):
                return ret_val.evaluate()
            else: #! This might cause some problems, be aware!
                return ret_val
        else:
            logger.error(f'Jump label {label} does not exist, but you tried to jump to there!')
    
    def get(self, label) -> object:
        if label in self.jumps.keys():
            return self.jumps[label]
        else:
            logger.error(f'Jump label {label} does not exist, but you tried to access it!')