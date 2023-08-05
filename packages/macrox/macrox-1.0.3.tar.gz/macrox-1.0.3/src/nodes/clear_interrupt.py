from nodes import bases
import globals

class ClearInterruptNode(bases.InstructionNode):
    KIND = 'ClearInterruptNode'
    def __init__(self) -> None:
        pass

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        globals.IM.kill_all()