from utils import logger

class DualStack():
    def __init__(self) -> None:
        self.instance_list = []
        self.body_list = []
    
    def push(self, instance: object, body: list):
        self.instance_list.append(instance)
        self.body_list.append(body.copy())

    def pop(self):
        if len(self.instance_list) > 0:
            instance = self.instance_list[-1]
            self.instance_list.pop()
            body = self.body_list[-1]
            self.body_list.pop()

            return instance, body
        else:
            logger.error('Unexpected error: DualStack is empty and pop was called from parser!')
