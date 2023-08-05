from nodes import bases
from globals import VH, GAH

class AssignNode(bases.ForkNode):
    KIND = 'AssignNode'
    _pp_left = 'target'

    def __init__(self, _, target, right) -> None:
        self.left, self.target = target, target
        self.right = right

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        right = self.identifier_to_value(self.right)

        if isinstance(self.right, bases.Node):
            right = self.right.evaluate(ignore_int)
        
        if self.target.token == 'Identifier': # variable
            self.set_variable(self.target, right)
        else:
            self.set_global_argument(self.target, right)


    def set_variable(self, target, value):
        VH.set(target, value) # VH => VariableHandlers
    def set_global_argument(self, target, value):
        GAH.set(target, value) # GAH => GlobalArgumentHandler
