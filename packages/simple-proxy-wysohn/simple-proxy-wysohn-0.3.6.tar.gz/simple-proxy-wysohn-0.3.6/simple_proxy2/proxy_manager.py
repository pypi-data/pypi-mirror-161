import asyncio
import functools
import random
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from threading import Lock, Condition, RLock
from typing import Dict, List, Callable, Optional, Any

import requests
from requests import Response, Session

from simple_proxy2.data.proxy_info import ProxyInfo
from simple_proxy2.pool.proxy_pool import ProxyPool
from simple_proxy2.tools.random_user_agent import get_random as random_agent
from simple_proxy2.tools.simple_timer import SimpleTimer


class Task:
    def __init__(self, fn: Callable):
        self._fn = fn

        self._result = None
        self._started = False
        self._done = False
        self._mutex = RLock()
        self._condition = Condition(self._mutex)

    def get(self):
        with self._mutex:
            if self._done:
                return

            self._condition.wait()
            return self._result

    def __call__(self, *args):
        with self._mutex:
            if self._started:
                return

            self._started = True

            assert not self._done, "task is already finished"

            try:
                self._result = self._fn(*args)
                self._done = True
                self._condition.notify_all()
            except Exception as ex:
                print(ex)


class ProxyManager:
    def __init__(self,
                 test_url: str,
                 proxy_info_dict: Dict[str, List[str]],
                 num_executors=32,
                 concurrent_trials_per_session=32,
                 verbose=False,
                 new_session_fn=lambda: requests.Session(),):
        """
        Create a new proxy manager. The manager has the internal thread workers, so to make it properly
        work, use it as a context manager. ex) with ProxyManager(...) as proxy_manager: ...

        :param test_url: url to test the availability of the proxy servers
        :param proxy_info_dict: a dictionary of proxy servers. The key is the protocol, and the value is a list of the ip:port pairs
        :param num_executors: number of threads to use for the executor
        :param executor_queue_size: size of the executor queue
        :param verbose: whether to print the success rate
        :param new_session_fn: function to create a new session. By default, it creates a new requests.Session()
        """

        self._test_url = test_url
        self._proxy_info_dict = proxy_info_dict
        self._verbose = verbose
        self._new_session_fn = new_session_fn
        self._loop = asyncio.get_event_loop()

        self._pool = self._init_pool(proxy_info_dict)

        # self._executor_running = False
        self._executor_workers = num_executors
        self._concurrent_trials_per_session = concurrent_trials_per_session
        # self._executor_queue = Queue(executor_queue_size)
        self._executor = ThreadPoolExecutor(max_workers=self._executor_workers)

        self._metrics_lock = Lock()
        self._success = 0
        self._trials = 0

    def _init_pool(self, info_dict: Dict[str, List[str]]) -> ProxyPool:
        info_list = []
        for protocol, addresses in info_dict.items():
            for address in addresses:
                info_list.append(ProxyInfo(protocol, address))

        return ProxyPool(self._test_url, self.success_rate, info_list)

    def _on_success(self):
        with self._metrics_lock:
            self._trials += 1
            self._success += 1

    def _on_fail(self):
        with self._metrics_lock:
            self._trials += 1

    def success_rate(self):
        with self._metrics_lock:
            if self._trials < 1:
                return 0.0
            else:
                return self._success / self._trials

    def proxy_as_request_session(self,
                                 success_criterion: Callable[[Response], bool] = lambda response: True) -> Session:
        return SessionProxy(self, success_criterion)

    async def proxy_session(self,
                            fn: Callable[[Session, tuple], Optional[Any]],
                            callback_async: Callable[[
                                Optional[Any]], None] = lambda x: None,
                            exception_handle: Callable[[
                                ProxyInfo, Exception], None] = lambda info, ex: print(info, ex),
                            args: tuple = (),
                            wait=False):
        """
        Work on the given function using the randomly chosen Session from the proxy pool. 'fn' will be retried
        indefinitely until success in order to try all available proxies.

        :param fn: function to execute. If has arguments, put those in the 'args'
        :param callback_async: callback to be invoked after 'fn' is done. Return value from 'fn' will be used as
         parameters
        :param exception_handle: decide what to do when exception occurred
        :param args: arguments to pass to 'fn'
        :param wait: block the thread and wait for the 'fn' to finish.
        :return: if 'wait' is True, the return value of 'fn' will be returned; None otherwise
        """

        end_event = asyncio.Event()

        async def task_fn():
            success = False

            while not end_event.is_set() and not success:
                with await self._pool.poll() as proxy:
                    session = self._new_session_fn()

                    session.proxies.update(proxy.info().as_requests_dict())

                    timer = SimpleTimer()
                    try:
                        timer.start()
                        result_future = self._loop.run_in_executor(
                            self._executor, functools.partial(fn, session, *args))

                        while not result_future.done():
                            await asyncio.sleep(0.1)
                            if end_event.is_set():
                                result_future.cancel()
                                return None

                        result = await result_future
                        timer.stop()

                        if type(result) is tuple:
                            callback_async(*result)
                        else:
                            callback_async(result)

                        success = True
                        return result
                    except Exception as ex:
                        exception_handle(proxy.info(), ex)
                        continue
                    finally:
                        proxy.update_response_time(
                            timer.time_elapsed() if success else 999.0)

                        if success:
                            self._on_success()
                        else:
                            self._on_fail()

        # task = Task(task_fn)
        # self._executor_queue.put(task, True)

        futures = [asyncio.create_task(task_fn())
                   for _ in range(self._concurrent_trials_per_session)]
        done, pending = await asyncio.wait(futures,
                                           return_when=asyncio.FIRST_COMPLETED)
        end_event.set()
        for future in futures:
            if not future.done():
                future.cancel()

        future = next(iter(done))

        if self._verbose:
            print("success rate:", self.success_rate())

        if wait:
            try:
                return await future
            except Exception as ex:
                exception_handle(None, ex)

    async def start(self):
        self._loop.set_exception_handler(lambda loop, context: None)
        await self._pool.start()

    async def stop(self, forced_shutdown=False):
        self._executor.shutdown(wait=True, cancel_futures=True)

        await self._pool.end()
        self._loop.set_exception_handler(None)

    def __enter__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.stop(exc_type is not None))

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.stop(exc_type is not None)


class SessionProxy(Session):
    def __init__(self, manager: ProxyManager, success_criterion):
        super().__init__()

        self._manager = manager
        self._success_criterion = success_criterion

    def request(self, method, url,
                params=None, data=None, headers=None, cookies=None, files=None,
                auth=None, timeout=None, allow_redirects=True, proxies=None,
                hooks=None, stream=True, verify=None, cert=None, json=None):

        def fn(session: Session):
            if headers is not None:
                session.headers.update(headers)

            response = session.request(method, url,
                                       params, data, headers, cookies, files,
                                       auth, timeout, allow_redirects, None,
                                       hooks, stream, verify, cert, json)

            if not self._success_criterion(response):
                raise Exception(
                    "Response does not satisfy the success criterion.")

            return response

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._manager.proxy_session(fn, wait=True))
