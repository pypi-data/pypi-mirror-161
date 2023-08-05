class GlobalArgumentHandler():
    def __init__(self, vh) -> None:
        self.variable_handler = vh
        self.arguments = {}


    def set(self, name, value):
        self.arguments[name[1:]] = self.identifier_to_value(value).part # strip the "%" from the name

    def get_list(self):
        return self.arguments
    
    def get(self, name):
        return self.arguments[name]

    def identifier_to_value(self, ast):
        if isinstance(ast, str):
            if ast.startswith('$'):
                return self.variable_handler.get(ast)

        return ast