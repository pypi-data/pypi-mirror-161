import threading
import globals
from utils import logger

def print_threads():
    globals.IM.pause_all()

    logger.info(15*'=' + ' Threads ' + 15*'=')
    for i, thread in enumerate(threading.enumerate()): 
        logger.info(f'[{i}] - {thread.name}')
    logger.info(39*'=')

    globals.IM.resume_all()

def print_vars():
    globals.IM.pause_all()

    vars = globals.VH.variables
    logger.info(14*'=' + ' Variables ' + 14*'=')
    for i, key in enumerate(vars):
        logger.info(f'[{i}] - {key} : {vars[key]}')
    logger.info(39*'=')
    
    globals.IM.resume_all()