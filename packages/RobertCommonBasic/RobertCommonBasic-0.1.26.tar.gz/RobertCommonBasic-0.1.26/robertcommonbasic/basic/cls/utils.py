
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from func_timeout import func_timeout
from func_timeout.exceptions import FunctionTimedOut
from multiprocessing import Pool
from queue import Queue
from threading import Thread, Lock, Timer, Condition
from typing import Callable, Optional, Union


class Singleton(type):
    _instance_lock = Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with Singleton._instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


'''
#元类
class SingClass(metaclass=Singleton):
    def __init__(self):
        pass
'''


class SingleInstance(object):
    _instance_lock = Lock()
    _instance = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SingleInstance, '_instance'):
            with SingleInstance._instance_lock:
                if not hasattr(SingleInstance, '_instance'):
                    SingleInstance._instance = SingleInstance(*args, **kwargs)
        return SingleInstance._instance


def daemon_thread(fn: Callable) -> Callable[..., Thread]:

    @wraps(fn)
    def _wrap(*args, **kwargs) -> Thread:
        return Thread(target=fn, args=args, kwargs=kwargs, daemon=True)

    return _wrap


def function_thread(fn: Callable, daemon: bool, *args, **kwargs):
    return Thread(target=fn, args=args, kwargs=kwargs, daemon=daemon)


def set_timeout_wrapper(timeout):
    def inner_set_timeout_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func_timeout(timeout, func, args=args, kwargs=kwargs)
            except FunctionTimedOut as e:
                raise Exception(f'func({func.__name__}) time out')
            except Exception as e:
                raise e
        return wrapper
    return inner_set_timeout_wrapper


class RepeatingTimer(Timer):

    '''
     @daemon_thread
        def thread_func():
            pass
    '''

    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


class SimpleTimer():

    def __init__(self):
        self.timer = None

    def is_running(self):
        return self.timer and self.timer.is_alive()

    def run(self, interval: int, function: Callable, args=None, kwargs=None):
        if self.is_running():
            if kwargs.get('force', False) is False:
                raise Exception(f"timer is running, please cancel")
            else:
                self.cancel()
        self._run_timer(interval, function, args, kwargs)

    def _run_timer(self, interval: int, function: Callable, args=None, kwargs=None):
        self.timer = Timer(interval, function, args, kwargs)
        self.timer.start()

    def cancel(self):
        if self.is_running():
            self.timer.cancel()
        self.timer = None


class RepeatThreadPool:

    def __init__(self, size: int, fun: Optional[Callable] = None, done_callback: Optional[Callable] = None, **kwargs):
        self.kwargs = kwargs
        self.pool_size = size              # 线程池大小
        self.pool_fun = fun                # 线程函数
        self.pools = ThreadPoolExecutor(self.pool_size) # 线程池
        self.done_callback = done_callback              # 线程执行回调函数

        self.task_queue = Queue()               # 待处理队列
        self.task_cache = {}                    # 全部任务
        self.task_running = {}                  # 正在处理任务
        self.pool_status = 'running'
        self.task_finish: int = 0               # 已完成任务

    def __del__(self):
        self.pools.shutdown()
        self.pool_status = 'shutdown'

    def process_task(self):
        if self.task_queue.empty() is False and len(self.task_running) <= self.pool_size:
            task_index = self.task_queue.get()
            if isinstance(task_index, int) and task_index > 0:
                task_info = self.task_cache.get(task_index)
                if isinstance(task_info, dict):
                    task_info['process'] = time.time()
                    future = self.pools.submit(task_info.get('task'), *(task_info.get('args')))
                    self.task_running[future] = task_index
                    future.add_done_callback(self.future_callback)

    def add_task(self, task, task_back, *args, **kwargs) -> int:
        index = len(self.task_cache) + 1
        self.task_cache[index] = {'index': index, 'create': time.time(), 'task': task, 'task_back': task_back, 'args': args, 'kwargs': kwargs}
        self.task_queue.put(index)
        return index

    def submit_task(self, task: Optional[Callable], task_back: Optional[Callable], *args, **kwargs) -> int:
        if len(args) > 0:
            task = task if task else self.pool_fun
            task_back = task_back if task_back else self.done_callback
            task_index = self.add_task(task, task_back, *args, **kwargs)
            self.process_task()
            return task_index
        return 0

    def reactive_task(self, future):
        if future is not None and future in self.task_running.keys():
            del self.task_running[future]

        # 触发响应
        self.process_task()

    def future_callback(self, future):
        self.task_finish = self.task_finish + 1
        if future in self.task_running.keys():
            task_info = self.task_cache.get(self.task_running[future])
            if isinstance(task_info, dict):
                task_info['future'] = future
                task_info['result'] = future.result()
                task_info['end'] = time.time()
                task_info['cost'] = '{:.3f}'.format(task_info['end'] - task_info['process'])
                done_callback = task_info.get('task_back')
                if done_callback:
                    done_callback(task_info)

    def finish(self) -> bool:
        if self.task_queue.empty() is True and len(self.task_running) == 0:
            self.pool_status = 'finish'
            return True
        return False

    def done(self):
        while self.finish() is False:
            time.sleep(1)

    def status(self):
        return self.pool_status

    def info(self):
        return {'total': len(self.task_cache), 'running': len(self.task_running), 'finish': self.task_finish}


class SimpleThreadPool:

    def __init__(self, size: int, fun: Optional[Callable] = None, done_callback: Optional[Callable] = None, **kwargs):
        self.kwargs = kwargs
        self.pool_size = size              # 线程池大小
        self.pool_fun = fun                # 线程函数
        self.pools = ThreadPoolExecutor(self.pool_size) # 线程池
        self.done_callback = done_callback              # 线程执行回调函数
        self.task_future = []

    def submit_task(self, task: Optional[Callable], *args, **kwargs):
        task = task if task else self.pool_fun
        if task is not None:
            self.task_future.append(self.pools.submit(task, *args, **kwargs))

    def done(self, dict_result: bool = True):
        results_dict = {}
        results_list = []
        for future in as_completed(self.task_future):
            result = future.result()
            if result is not None:
                if isinstance(result, dict):
                    results_dict.update(result)
                elif isinstance(result, list):
                    results_list.extend(result)
                else:
                    results_list.append(result)
        return results_dict if dict_result else results_list


class ThreadPool:

    def __init__(self, pool_size: int, pool_fun: Callable, fun_params: list):
        self.pool_size = pool_size
        self.pool_fun = pool_fun
        self.fun_params = fun_params
        self.pool_cost = 0

    def run(self, dict_result: bool = True):
        start = time.time()
        with ThreadPoolExecutor(self.pool_size) as executor:
            futures = [executor.submit(self.pool_fun, *fun_param) for fun_param in self.fun_params]

        results_dict = {}
        results_list = []
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                if isinstance(result, dict):
                    results_dict.update(result)
                elif isinstance(result, list):
                    results_list.extend(result)
                else:
                    results_list.append(result)

        self.pool_cost = '{:.3f}'.format(time.time() - start)
        return results_dict if dict_result else results_list

    def cost(self):
        return self.pool_cost


class MultiPool:

    def __init__(self, pool_size: int, pool_fun: Callable, fun_params: list):
        self.pool_size = pool_size
        self.pool_fun = pool_fun
        self.fun_params = fun_params
        self.pool_cost = 0

    def run(self, dict_result: bool = True):
        start = time.time()
        results_dict = {}
        results_list = []
        with Pool(self.pool_size) as p:
            p.map(self.pool_fun, self.fun_params)

            for result in p.imap_unordered(self.pool_fun, self.fun_params):
                if result is not None:
                    if isinstance(result, dict):
                        results_dict.update(result)
                    elif isinstance(result, list):
                        results_list.extend(result)
                    else:
                        results_list.append(result)

        self.pool_cost = '{:.3f}'.format(time.time() - start)
        return results_dict if dict_result else results_list

    def cost(self):
        return self.pool_cost


class WaitQueue:

    def __init__(self, lock=None):
        self.condition = Condition(lock)
        self.values = []

    def wait(self, timeout: Union[int, float, None] = None):
        with self.condition:
            return self._wait(timeout)

    def _wait(self, timeout: Union[int, float, None] = None):
        self.condition.wait(timeout)

    def notify_all(self, value=None):
        with self.condition:
            if value is not None:
                self.values.append(value)
            self.condition.notify_all()

    def notify(self, value=None, n: int=1):
        with self.condition:
            if value is not None:
                self.values.append(value)
            self.condition.notify(n)