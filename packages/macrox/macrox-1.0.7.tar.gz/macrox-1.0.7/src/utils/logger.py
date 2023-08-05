import colorama

colorama.init()

def pprint(message, tag, tag_color, command=None):
    if command:
        command = command.upper()
        print(f'[{tag_color}{tag}{colorama.Style.RESET_ALL}]  [@{colorama.Fore.CYAN}{command}{colorama.Style.RESET_ALL}]  {message}')
    else:
        print(f'[{tag_color}{tag}{colorama.Style.RESET_ALL}]  {message}')

def error(message, command=None):
    pprint(message=message, command=command, tag="ERRO", tag_color=colorama.Fore.RED)
    exit()

def info(message, command=None):
    pprint(message=message, command=command, tag="INFO", tag_color=colorama.Fore.BLUE)

def warning(message, command=None):
    pprint(message=message, command=command, tag="WARN", tag_color=colorama.Fore.YELLOW)

