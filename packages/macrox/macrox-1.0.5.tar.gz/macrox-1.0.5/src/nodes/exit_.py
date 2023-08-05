import imp
from nodes import bases
from utils import terminate

class ExitNode(bases.InstructionNode):
    KIND = 'ExitNode'
    def __init__(self) -> None:
        pass

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        terminate.terminate()