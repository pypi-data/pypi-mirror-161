import logging
from logging import Formatter, StreamHandler, Logger
import traceback

__logger_map = {
    logging.INFO: 'info',
    logging.DEBUG:'debug',
    logging.WARN: 'warn',
    logging.ERROR: 'error',
    logging.NOTSET:'info',
}

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_print = print
globals()['print'] = _print

def __create_log(name, print_level, level):
    log = Logger(name, print_level)
    h = StreamHandler()
    h.setLevel(level)
    log.addHandler(h)
    return log, h

__print_stack = []
__logger_stack = []

def xprint(
    print_level=DEBUG,
    level=DEBUG,
    disable=False
):
    def print_wrap(func):
        def func_wrap(*args):
            if 'print' not in func.__globals__:
                func.__globals__['print'] = _print
            g = func.__globals__
            if not disable:
                __logger_stack.append(__create_log(str(len(__print_stack)), print_level, level))
            def log(*args):
                args = ' '.join([str(i) for i in args])
                logger, h = __logger_stack[-1]
                trace = traceback.extract_stack()[-2]
                fmt = '[%s:%d - %s][%s] - ' % (
                        trace.filename,
                        trace.lineno,
                        trace.name,
                        logging._levelToName[print_level]
                )
                fmt += '%(msg)s'
                h.setFormatter(Formatter(fmt))
                getattr(logger, __logger_map[print_level], logging.info)(args)
            if not disable:
                __print_stack.append(log)
            if not disable:
                g['print'] = log
            if disable:
                prev_handle = g['print']
                g['print'] = _print
            ret = func(*args)
            if disable:
                g['print'] = prev_handle
            if not disable:
                __logger_stack.pop()
                if not __logger_stack:
                    g['print'] = _print
                else:
                    g['print'] = __print_stack.pop()
            return ret
        return func_wrap
    return print_wrap
