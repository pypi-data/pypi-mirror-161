from nodes import bases

class Root(bases.BlockNode):
    KIND = 'RootNode'
    def __init__(self):
        self.body = []

    def evaluate(self, ignore_int = False):
        for node in self.body:
            super().evaluate(ignore_int)
            node.evaluate()