from utils import logger
import globals
import os

def terminate():
    globals.IM.kill_all()
    os._exit(1)

def terminate_by_hand():
    globals.IM.pause_all()

    logger.info('')
    logger.info('+' + 29*'-' + '+')
    logger.info('|' + 29*' ' + '|')
    logger.info('| You terminated the program! |')
    logger.info('|' + 29*' ' + '|')
    logger.info('+' + 29*'-' + '+')
    logger.info('')

    terminate()

def terminate_recording():
    logger.info('Recording was terminated!')
    os._exit(1)