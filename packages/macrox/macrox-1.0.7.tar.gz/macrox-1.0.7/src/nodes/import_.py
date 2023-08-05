from nodes import bases
import globals
import os

class ImportNode(bases.InstructionNode):
    KIND = 'ImportNode'
    def __init__(self, module) -> None:
        self.module = module

    def evaluate(self, ignore_int = False):
        super().evaluate(ignore_int)
        abs_path = __file__.replace('/nodes/import_.py', '', 1).replace('\\nodes\\import_.py', '', 1)
        globals.Importer.import_module(f'{abs_path}/commands/{self.module}/')