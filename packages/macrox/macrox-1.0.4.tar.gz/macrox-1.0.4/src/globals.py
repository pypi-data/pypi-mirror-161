from utils import variable_handler, jump_handler, importer, global_argument_handler, interrupt_queue, interrupt_manager

VH = variable_handler.VariableHandler()
JH = jump_handler.JumpHandler()
GAH = global_argument_handler.GlobalArgumentHandler(vh=VH)
Importer = importer.Importer()
IQ = interrupt_queue.InterruptQueue()
IM = interrupt_manager.InterruptManager()

break_bool = False