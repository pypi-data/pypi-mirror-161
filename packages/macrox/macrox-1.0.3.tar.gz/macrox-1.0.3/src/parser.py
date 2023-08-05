import nodes
from utils import logger
from globals import JH, IM
from tokens.base_token import Token
from utils.dualstack import DualStack

class Parser():
    SEARCH_FORS = {
        'Add': nodes.BinaryOperations,
        'Minus': nodes.BinaryOperations,
        'Times': nodes.BinaryOperations,
        'Divide': nodes.BinaryOperations,
        'Assign': nodes.AssignNode,
        'Equals': nodes.LogicalOperations,
        'NotEquals': nodes.LogicalOperations,
        'Greater': nodes.LogicalOperations,
        'Less': nodes.LogicalOperations,
        'GreaterEquals': nodes.LogicalOperations,
        'LessEquals': nodes.LogicalOperations,
        'While': nodes.WhileNode,
        'If': nodes.IfNode,
        'ElseIf': nodes.IfNode,
        'Else': None,
        'OpenCurlyBracket': None,
        'CloseCurlyBracket': None,
        'Break': nodes.BreakNode,
        'Label': nodes.LabelNode,
        'Jump': nodes.JumpNode,
        'Call': nodes.CallNode,
        'Sleep': nodes.SleepNode,
        'Import': nodes.ImportNode,
        'Interrupt': nodes.InterruptNode,
        'ClearInterrupt': nodes.ClearInterruptNode,
        'Exit': nodes.ExitNode,
        'Return': nodes.ReturnNode
    }

    def __init__(self, tokens) -> None:
        self.tokens = tokens

        self.body_flag = None
        self.block_ptr = None
        self.elif_cases = 0

    def parse(self) -> list: # Just sort tokens by priority. Then just parse normally without any complication
        self.body = []
        self.stack = DualStack()
        self.block_ptr = nodes.Root()

        self.tokens = self.preprocess(self.tokens)
        prev_i = 0
        for i, token in enumerate(self.tokens):
            if token.token == 'Newline':
                node = self.next_node(self.tokens[prev_i:i])
                if node != None:
                    self.body.append(node)
                if self.body_flag is False: # pop
                    special_case = False
                    if len(self.tokens)-1 > i:
                        special_case = self.tokens[i+1].token in ['ElseIf', 'Else', 'OpenCurlyBracket']
                    if not special_case: # check if pop needed
                        for _ in range(self.elif_cases+1):
                            self.block_ptr.set_body(self.body)
                            self.body.clear()

                            self.block_ptr, self.body = self.stack.pop()
                            self.body_flag = True

                        self.elif_cases = 0
                    else:
                        if self.tokens[i+1].token in ['ElseIf', 'Else']:
                            if self.tokens[i+1].token == 'ElseIf':
                                self.elif_cases += 1
                            self.block_ptr.set_body(self.body)
                            self.body.clear()

                prev_i = i+1

        self.block_ptr.set_body(self.body)
        return self.block_ptr

    def next_node(self, remaining_tokens: list) -> nodes.Node:
        for i, token in enumerate(remaining_tokens):
            for sftoken in self.SEARCH_FORS:
                if token.token is sftoken:  
                    if sftoken in ['If', 'While', 'ElseIf']:
                        if len(remaining_tokens[1:]) > 1:
                            cond = self.next_node(remaining_tokens[1:])
                        else:
                            cond = remaining_tokens[1].part

                        node = self.SEARCH_FORS[sftoken](cond)
                        self.body.append(node) # append sub-node to root-node
                        self.stack.push(self.block_ptr, self.body) # push
                        self.block_ptr = node
                        self.body.clear() # clear the current body list

                        return None

                    elif sftoken == 'Else': # I should do bug-checks here
                        pass
                    elif sftoken == 'Label':
                        node = self.SEARCH_FORS[sftoken]()
                        JH.setup_jump(token.part, node)

                        self.body.append(node) # append sub-node to root-node
                        self.stack.push(self.block_ptr, self.body) # push
                        self.block_ptr = node
                        self.body.clear() # clear the current body list
                    elif sftoken == 'OpenCurlyBracket':
                        self.body_flag = True
                        return None
                    elif sftoken == 'CloseCurlyBracket':
                        self.body_flag = False
                        return None
                    elif sftoken in ['Break', 'ClearInterrupt', 'Exit']:
                        return self.SEARCH_FORS[sftoken]()
                    elif sftoken in ['Jump', 'Sleep', 'Import']:
                        return self.SEARCH_FORS[sftoken](remaining_tokens[1].part)
                    elif sftoken == 'Return':
                        if len(remaining_tokens[1:]) > 1: # or remaining_tokens[1].token == 'Call':
                            val = self.next_node(remaining_tokens[1:])
                        else:
                            val = remaining_tokens[1]
                        return nodes.ReturnNode(value=val)
                    elif sftoken == 'Call':
                        return nodes.CallNode(token.part, remaining_tokens[1:])
                    elif sftoken == 'Interrupt':
                        if len(remaining_tokens[2:]) > 1: # or remaining_tokens[2].token == 'Call':
                            cond = self.next_node(remaining_tokens[2:])
                        else:
                            cond = remaining_tokens[2]
                        int_node = nodes.InterruptNode(remaining_tokens[1].part, cond)
                        IM.add(int_node)

                        return int_node
                    else:
                        if i+1 > 2:
                            logger.error(f'Unknown operation, the parser missed something at line: {remaining_tokens}')

                        node = self.SEARCH_FORS[sftoken]
                        
                        op = token.token
                        left = remaining_tokens[i-1]

                        if len(remaining_tokens[i+1:]) > 1 or remaining_tokens[2].token == 'Call':
                            right = self.next_node(remaining_tokens[i+1:]) # 1.: right, 2.: operation, ... etc.
                        else:
                            right = remaining_tokens[2]
                        return node(op, left, right) # Returns a non-evaluated node object

    def preprocess(self, tokens):
        tokens = self.sort_tokens(tokens)
        if not self.sanity_check(tokens):
            logger.error('Parser\'s sanity check failed!')
        
        ret_tokens = []
        for i, token in enumerate(tokens):
            if token.token == 'OpenCurlyBracket':
                ret_tokens.append(Token('Newline', '\\n'))
                ret_tokens.append(token)
                ret_tokens.append(Token('Newline', '\\n'))
                
            elif token.token == 'CloseCurlyBracket':
                ret_tokens.append(Token('Newline', '\\n'))
                ret_tokens.append(token)
                ret_tokens.append(Token('Newline', '\\n'))
            else:
                ret_tokens.append(token)

        return ret_tokens

    def sort_tokens(self, token_list: list) -> list: # TODO: Finish this!!
        return token_list
    
    def sanity_check(self, tokens) -> bool: # TODO: Finish this!!
        return True
