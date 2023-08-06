import asyncio
import requests

from queue import PriorityQueue
from threading import Thread
from typing import List, Callable

from simple_proxy2.data.observer import Observer
from simple_proxy2.data.proxy import Proxy
from simple_proxy2.data.proxy_info import ProxyInfo
from simple_proxy2.tools.simple_timer import SimpleTimer
from simple_proxy2.tools.random_user_agent import get_random as random_agent


class ProxyPool(Observer):
    def __init__(self,
                 test_url: str,
                 success_rate_supplier: Callable[[], float],
                 proxy_infos: List[ProxyInfo]):
        self._test_url = test_url
        self._success_rate_supplier = success_rate_supplier
        self._pool = PriorityQueue()
        self._proxy_infos = proxy_infos

    async def _init_proxy(self, proxy_infos: List[ProxyInfo]):
        assert len(
            proxy_infos) > 0, "At least one proxy must exist for ProxyPool to work properly."

        for info in proxy_infos:
            proxy = Proxy(info, self._success_rate_supplier)
            proxy.register_observer(self)
            proxy.update_response_time(999.0)

            self._pool.put(proxy)

    async def poll(self) -> Proxy:
        return self._pool.get()

    def notify(self, proxy: Proxy):
        self._pool.task_done()
        self._pool.put(proxy)

    async def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self._init_proxy(self._proxy_infos))

    async def end(self):
        pass

    def __enter__(self):
        self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
