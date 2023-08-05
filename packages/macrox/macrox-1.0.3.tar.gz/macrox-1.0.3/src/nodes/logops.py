from nodes import bases
from utils import logger
from tokens import base_token
import globals

class LogicalOperations(bases.ForkNode):
    KIND = 'LogicalOperationsNode'
    def __init__(self, op, left, right):
        self.op = op
        self.right = right
        self.left = left

        self.KIND = f'{self.op}Node'

    def conv_num(self, num, ignore_int) -> int|float|str|bool|None:
        if isinstance(num, bases.Node):
            return num.evaluate(ignore_int)
        elif isinstance(num, base_token.Token):
            if num.token == 'LabelName':
                return self.conv_num(self.identifier_to_value(globals.JH.jump(num.part[1:], ignore_int)), ignore_int) # conv_num might not be needed here
            elif num.token == 'Number':
                return num.part
            elif num.token == 'Float':
                return num.part
            elif num.token == 'HexNumber':
                return int(num.part, base=16)
            elif num.token == 'BinaryNumber':
                return int(num.part.replace('0b', '', 1), base=2)
            elif num.token == 'String':
                if num.part == 'true':
                    return True
                elif num.part == 'false':
                    return False
                try:
                    return int(num.part)
                except:
                    pass
                try:
                    return float(num.part)
                except:
                    pass
                return num.part
            elif num.token == 'Boolean':
                return num.part
       
        logger.error(f'Did not recognize the following value: {num}')

    def get_type(self, target) -> str:
        if isinstance(target, bool):
            return 'Bool'
        elif isinstance(target, int) or isinstance(target, float):
            return 'Num'
        elif isinstance(target, str):
            return 'String'
        


    def evaluate(self, ignore_int = False) -> bool:
        super().evaluate(ignore_int)
        left = self.conv_num(self.identifier_to_value(self.left), ignore_int)
        if isinstance(self.right, bases.Node):
            right = self.right.evaluate()
        else:
            right = self.conv_num(self.identifier_to_value(self.right), ignore_int)
        
        type_l = self.get_type(left)
        type_r = self.get_type(right)
        
        if type_l != type_r:
            logger.error(f'Can\'t use logical operation "{self.op}" on {type_l} and {type_r}!')

        if self.op == 'Equals':
            if left == right:
                return True
            return False

        elif self.op == 'NotEquals':
            if left != right:
                return True
            return False
        
        if type_l == 'Bool' or type_l == 'String':
            logger.error(f'Can\'t use operation {self.op} on {type_l}')


        if self.op == 'Greater':
            if left > right:
                return True
            return False

        elif self.op == 'Less':
            if left < right:
                return True
            return False
        
        elif self.op == 'GreaterEquals':
            if left >= right:
                return True
            return False
        
        elif self.op == 'LessEquals':
            if left <= right:
                return True
            return False

    