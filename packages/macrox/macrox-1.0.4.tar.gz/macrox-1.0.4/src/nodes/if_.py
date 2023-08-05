from textwrap import indent
from utils import logger
from nodes import bases

class IfNode(bases.Node):
    KIND = 'IfNode'
    def __init__(self, condition):
        self.condition = condition

        self.if_body = None
        self.else_body = None

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        if isinstance(self.condition, bases.Node):
            cond = self.condition.evaluate()
            if cond == True:
                return self.evaluate_body(self.if_body)
            elif cond == False:
                return self.evaluate_body(self.else_body)
        else:
            cond = self.identifier_to_value(self.condition).part
            if cond == True:
                return self.evaluate_body(self.if_body)
            elif cond == False:
                return self.evaluate_body(self.else_body)
    

    def evaluate_body(self, body):
        if isinstance(body, list):
            for node in body:
                ret_val = node.evaluate()
                if ret_val is not None:
                    return ret_val
        elif isinstance(body, bases.Node):
            body.evaluate()

    def set_body(self, body: list[bases.Node]):
            if self.if_body == None:
                self.if_body = body.copy()
            else:
                self.else_body = body.copy()

    def prettyprint(self, indent):
        indent_str = ' '*indent
        condition = self.condition
        if isinstance(condition, bases.ForkNode):
            condition = condition.prettyprint(indent=(indent+4))



        return f'{self.KIND} (\n{indent_str}    Condition: {condition}\n{indent_str}    If-Body: {self.pprint_body(self.if_body, indent)}\n{indent_str}    Else-Body: {self.pprint_body(self.else_body, indent)}\n{indent_str})'

    def pprint_body(self, body, indent: int) -> str:
        ret_str = ''
        if isinstance(body, list):
            for node in body:
                ret_str += node.prettyprint(indent=indent+4)
        elif isinstance(body, IfNode):
            ret_str += body.prettyprint(indent=indent+4)
        
        return ret_str