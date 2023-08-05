from nodes import bases

class LabelNode(bases.BlockNode):
    KIND = 'LabelNode'
    def __init__(self) -> None:
        self.body = []

    def evaluate(self, jump=False, ignore_int = False):
        super().evaluate(ignore_int)
        if jump:
            for node in self.body:
                super().evaluate(ignore_int)
                ret_val = node.evaluate(ignore_int)
                if ret_val is not None:
                    return ret_val