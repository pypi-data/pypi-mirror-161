class Token():
    def __init__(self, token_type, part):
        self.token = token_type
        
        if token_type == 'DecimalNumber':
            self.part = int(part)
        elif token_type == 'String':
            self.part = part[1:-1].replace('\\n', '\n')
        elif token_type == 'Boolean':
            if part.lower() == 'false':
                self.part = False
            else:
                self.part = True
        else:
            self.part = part

    def __repr__(self) -> str:
        if self.token:
            return f"Token <{self.token}> <{self.part}>"
        else:
            return "Token <NONE> <NONE>"
        
    def __str__(self) -> str:
        return self.__repr__()

    
