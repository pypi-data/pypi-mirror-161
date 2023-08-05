from nodes import bases
from utils import logger

class ReturnNode(bases.InstructionNode):
    KIND = 'ReturnNode'
    def __init__(self, value: int) -> None:
        self.value = value

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        
        if isinstance(self.value, bases.Node):
            value = self.value.evaluate()
        else:
            value = self.value
        
        return value

    def prettyprint(self, indent):
        indent_str = ' '*indent
        return f'{self.KIND} (\n{indent_str}    Value: {str(self.value)}ms\n{indent_str})'