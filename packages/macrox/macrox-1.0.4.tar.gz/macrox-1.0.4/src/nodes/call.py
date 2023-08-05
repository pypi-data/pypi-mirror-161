from nodes import bases
from tokens import base_token
from utils import logger
from globals import Importer, GAH

class CallNode(bases.Node):
    KIND = 'CallNode'
    def __init__(self, command: str, arguments: list) -> None:
        self.command = command[1:]
        self.arguments = arguments

        self.check_raw_sequence()

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        args_dict = {}

        ga_list = GAH.get_list()
        command_class = Importer.get_command(self.command)
        global_match = False

        for arg in command_class.arg_parse_list:
            if arg in ga_list:
                global_match = True  
                args_dict[arg] = ga_list.get(arg)

        args_dict.update(self.create_dict(self.arguments))
        if global_match:
            self.check_sequence(args_dict)

        command_object = command_class(args_dict)
        ret = command_object.run()

        return ret 


    def create_dict(self, args: list):
        ret_dict = {}
        counter = 0
        skip_flag = False

        for i, token in enumerate(args):
            if skip_flag:
                skip_flag = False
                continue
            if token.token == 'KeywordArgument': 
                ret_dict[token.part[:-1].strip()] = self.identifier_to_value(args[i+1]).part
                skip_flag = True
            else:
                ret_dict[counter] = self.identifier_to_value(token).part
                counter += 1

        return ret_dict

    def check_sequence(self, args):
        kwarg = False
        for element in args.keys():
            if isinstance(element, str):
                kwarg = True
            else:
                if kwarg:
                    logger.error('You tried to use a regular argument with global arguments! That\'s a no go! Use keyword arguments instead!')

    def check_raw_sequence(self):
        key_argument_flag = False
        skip_flag = False

        for token in self.arguments:
            if skip_flag:
                skip_flag = False
                continue
            if token.token == 'KeywordArgument':
                skip_flag = True
                key_argument_flag = True
            else:
                if key_argument_flag:
                    logger.error('You tried to use a regular argument after a keyword argument! That\'s a no go!')
    
    def prettyprint(self, indent):
        indent_str = ' '*indent

        return f'{self.KIND} (\n{indent_str}    Command: {self.command}\n{indent_str}    Arguments: {self.arguments}\n{indent_str})'
