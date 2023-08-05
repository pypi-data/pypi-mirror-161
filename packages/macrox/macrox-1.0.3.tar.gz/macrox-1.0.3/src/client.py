import textwrap
import interpreter
import keyboard
from utils import terminate, debugger, recorder, options
import argparse

def main():
    DESC = '''
        A python macro program!

        Features:
         - Low-level syntax programming language
         - Mouse & Keyboard event recording
         - Python-MacroX API (you can create commands in python and run it in MacroX)
        
        Please keep in mind that this scripting language is a one-dev project, any help is appreciated!
        If you find any bugs please report at the github issues section.

        Official Source: https://github.com/Wrench56/MacroX/        
    '''

    parser = argparse.ArgumentParser(prog='MacroX',  formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent(DESC))
    
    parser.add_argument('--record', dest='record', action='store_true', 
                    help='Record mouse & click actions to replay it later', default=False)
    parser.add_argument('filename', action='store', 
                    help='Specify a filename to run / to save the recording', nargs='?')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                    help='Print every processing step (tokenize, parse, etc...)')
    

    options.options = parser.parse_args()
    if options.options:
        if options.options.filename is not None:
            keyboard.add_hotkey('ctrl+q', terminate.terminate_recording)
            rec = recorder.Recorder()
            rec.wait_for('f1', options.options.filename + '.mof')
    else:
        keyboard.add_hotkey('ctrl+q', terminate.terminate_by_hand)
        keyboard.add_hotkey('ctrl+t', debugger.print_threads)
        keyboard.add_hotkey('ctrl+v', debugger.print_vars)

        Interpreter = interpreter.Interpreter(path=options.options.filename)
        Interpreter.start()



if __name__ == '__main__':
    main()