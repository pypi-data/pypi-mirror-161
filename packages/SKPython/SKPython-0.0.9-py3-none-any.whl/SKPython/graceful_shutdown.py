import signal
import types
import logging
import time

__callbacks = []
__is_shutdown = False
__shutdown_sleep_time = 30

def add_shutdown_callback(callback: types.FunctionType, *args, **kwargs):
    """
    종료 시그널이 발생했을 때 사용할 함수를 등록한다
    SIGTERM, SIGINT인 경우에 동작
    """
    __check_function_type(callback)
    __callbacks.append((callback, args, kwargs))
    if len(__callbacks) == 1:
        signal.signal(signal.SIGTERM, __graceful_shutdown)
        signal.signal(signal.SIGINT, __graceful_shutdown)

def is_pending():
    return __is_shutdown == False

def set_shutdown_sleep_time(seconds: int):
    global __shutdown_sleep_time
    __shutdown_sleep_time = seconds

def clear_shutdown_callback():
    __callbacks.clear()

def __graceful_shutdown(signum, frame):
    global __is_shutdown
    __is_shutdown = True
    
    logging.info(f"graceful shutdown: signum: {signum}, frame: {frame}")
    for func in __callbacks:
        args_len = len(func[1])
        kwargs_len = len(func[2])
        if args_len > 0 and kwargs_len > 0:
            func[0](*func[1], **func[2])
        elif args_len > 0:
            func[0](*func[1])
        elif kwargs_len > 0:
            func[0](**func[2])
        else:
            func[0]()
    
    time.sleep(__shutdown_sleep_time)
    raise RuntimeError("server shutdown")


def __check_function_type(func):
    if not (isinstance(func, types.MethodType) or isinstance(func, types.FunctionType)):
        raise GkNotValidTypeError(f"type: {type(func)} - 함수만 등록해주세요")


class GkNotValidTypeError(Exception):
    def __init__(self, message):
        super().__init__(message)