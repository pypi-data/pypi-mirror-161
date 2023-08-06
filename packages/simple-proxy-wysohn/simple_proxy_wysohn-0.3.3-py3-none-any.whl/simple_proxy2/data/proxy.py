import functools
import os
from typing import Callable

from simple_proxy2.data.observable import Observable
from simple_proxy2.data.proxy_info import ProxyInfo

delta = float(os.getenv('PROXY_MANAGER_DELTA', '0.00001'))
count_diff = int(os.getenv('PROXY_MANAGER_COUNT_DIFF', '0'))
use_count_per_success = int(
    os.getenv('PROXY_MANAGER_USE_COUNT_PER_SUCCESS', '1'))
use_count_per_failure = int(
    os.getenv('PROXY_MANAGER_USE_COUNT_PER_FAILURE', '5'))


@functools.total_ordering
class Proxy(Observable):
    def __init__(self, proxy_info: ProxyInfo, success_rate_supplier: Callable[[], float]):
        super().__init__()
        self._proxy_info = proxy_info
        self._success_rate_supplier = success_rate_supplier

        self._response_time = 999.0
        self._fail_count = 0
        self._use_count = 0

    def _fail(self):
        self._fail_count += use_count_per_failure

    def _close(self):
        # return this proxy to the pool
        self._notify_observers()

    def info(self):
        return self._proxy_info

    def update_response_time(self, new_time: float):
        self._response_time = new_time

    def failure_rate(self):
        if self._use_count == 0:
            return 0.0

        return self._fail_count / self._use_count

    def __eq__(self, other):
        response_difference = abs(self._response_time - other._response_time)

        return \
            response_difference < delta \
            and self._fail_count == other._fail_count \
            and self._use_count == other._use_count

    def __lt__(self, other):
        if count_diff > 0:
            # if the use count differ too much, the pool isn't cycling efficiently
            # give the other proxy chance to work
            fail_rate = 1 - self._success_rate_supplier()
            # if fail_rate is high, increase the re-use rate
            # if fail_rate is low, decreate the re-use rate
            if self._use_count - other._use_count > count_diff * fail_rate:
                return False
            elif self._use_count - other._use_count < -count_diff * fail_rate:
                return True

        self_fail_rate = self.failure_rate()
        other_fail_rate = other.failure_rate()

        # if 'this' fail rate is more than 'other' fail rate by the delta,
        # other proxy has better success rate
        if self_fail_rate - other_fail_rate > delta:
            return False
        elif self_fail_rate - other_fail_rate < -delta:
            return True

        # if usage and fail rate is similar, sort by response time
        return self._response_time < other._response_time

    def __enter__(self):
        assert len(self.observers) > 0, "No observers found."

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self._use_count += use_count_per_failure
                self._fail()
            else:
                self._use_count += use_count_per_success
        finally:
            self._close()

    def __repr__(self):
        return "proxy(info={}, response={}, fail={}, use={})".format(self._proxy_info,
                                                                     self._response_time,
                                                                     self._fail_count,
                                                                     self._use_count)
