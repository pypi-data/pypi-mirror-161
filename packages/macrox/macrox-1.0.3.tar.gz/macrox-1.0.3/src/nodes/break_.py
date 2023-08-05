from nodes import bases
import globals

class BreakNode(bases.InstructionNode):
    KIND = 'BreakNode'
    def __init__(self) -> None:
        pass

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        globals.break_bool = True