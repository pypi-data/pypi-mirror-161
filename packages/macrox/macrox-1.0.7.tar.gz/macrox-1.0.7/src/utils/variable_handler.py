from utils import logger

class VariableHandler():
    SYSTEM_VARIABLES = ['$TEST']
    def __init__(self):
        self.variables = {}
        self.system_variables()

    def system_variables(self):
        self.variables['$TEST'] = 'Hello'

    def set(self, target, value):
        if target.part not in self.SYSTEM_VARIABLES:
            self.variables[target.part] = value
        else:
            logger.error(f'Can\'t overwrite system variable {target}!')

    def get(self, target):
        if target.part in self.variables.keys():
            return self.variables[target.part]
        else:
            logger.error(f'Variable {target.part} is not yet initialized, but you tried to access it!')