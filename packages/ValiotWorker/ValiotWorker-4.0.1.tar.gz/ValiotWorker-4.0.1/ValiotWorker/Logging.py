# terminal styles for better logging
import sys
from enum import Enum
from colorama import Fore, Back, Style, init as init_term, AnsiToWin32
from termcolor import colored
# colorful terminal initializacion
init_term(wrap=True, autoreset=True)
stream = AnsiToWin32(sys.stderr).stream


class LogLevel(Enum):
    DEBUG = 'DEBUG'  # Blue
    ERROR = 'ERROR'  # Red
    INFO = 'INFO'   # White
    WARNING = 'WARNING'  # Yellow
    SUCCESS = 'SUCCESS'  # ! Green, Non-standard with Eliot (might not care)


class LogStyle(Enum):
    PREFIX_FIRST_LINE = 'PREFIX_FIRST_LINE'
    PREFIX_ALL_LINES = 'PREFIX_ALL_LINES'

# print wrappers


def log(level: LogLevel, message: str):
    """Logs formatted messages to stdout

    Parameters
    ----------
    level : LogLevel
        Message Level and color related to it (DEBUG, ERROR, etc, see LogLevel type)
    message : Any
        Message to log
    """
    if(level == LogLevel.INFO):
        log_info(message)
    if(level == LogLevel.SUCCESS):
        log_success(message)
    if(level == LogLevel.WARNING):
        log_warning(message)
    if(level == LogLevel.ERROR):
        log_error(message)
    if(level == LogLevel.DEBUG):
        log_debug(message)


def log_info(message):
    print(colored(message, 'white'))


def log_success(message):
    print(colored(message, 'green'))


def log_warning(message):
    print(colored(message, 'yellow'))


def log_error(message):
    print(colored(message, 'red'))


def log_debug(message):
    print(colored(message, 'blue'))


'''
# Multiprocessing Pipes reference (For inter-process communication):

# import multiprocessing as mp
# from multiprocessing import Pipe
# import time
# context = mp.get_context('fork')

# def fn_slow():
#   count = 5
#   while count:
#     count -= 1
#     time.sleep(1.0)

# pslow = context.Process(target=fn_slow)
# pslow.start()


kill = False
def fn(id, conn):
  started = time.time()
  while not kill:
    time.sleep(5.0)
    conn.send({
      'id': id,
      'level': 'DEBUG',
      'msg': f'Tick: {time.time() - started}'
    })

ps = []

CONN, conn = Pipe()
ps.append({
  'p': context.Process(target=fn, args=(len(ps)+1, conn,)),
  'c': CONN
})

ps[-1]['p'].start()
ps[-1]['p'].pid

try:
  while 1:
    _conn = ps[-1]['c']
    if _conn.poll():
      print(_conn.recv())
    time.sleep(0.1)
except KeyboardInterrupt:
  kill = True

ps[-1]['p'].join()

'''
