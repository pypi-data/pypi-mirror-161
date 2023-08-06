import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, RLock
from queue import PriorityQueue

import requests

from simple_proxy.proxy_info import ProxyInfo
from simple_proxy.user_agents import get_random_useragent

PROTOCOL = 'http'


class ProxyPool:
    def __init__(self, test_url, l_http, l_https, l_sock4, l_sock5,
                 fail_predicate_fn,
                 timeout=2,
                 connection_check_on_start=True,
                 num_top_proxies=100,
                 verbose=False):
        """
        Start a self-organizing proxy pool which consistently re-order the proxies based on the failure rate and
        response time. It uses requests for test.
        :param test_url: str
            the test_url to be used to measure the connection status and response time
        :param l_http: list
            list of http proxies. (ip:port separated by \n)
        :param l_https: list
            list of https proxies. (ip:port separated by \n)
        :param l_sock4: list
            list of socks4 proxies. (ip:port separated by \n)
        :param l_sock5: list
            list of socks5 proxies. (ip:port separated by \n)
        :param fail_predicate_fn: function
            the predicate function which return true given the Response instance of requests package.
        :param timeout: int
            request connection timeout.
        :param reuse_delay: int
            delay before reusing the proxy. This helps the pool to cycle proxy not only the few top proxies being
            used, but multiple proxies get chance to be used
        :param connection_check_on_start: bool
            check if the provided proxies are alive before being added to the pool
        :param cycle_proxy: bool
            cycle the proxy regardless of the pool order. You get to use every single proxies one-by-one
        :param verbose: bool
            print useful messages for debugging
        """

        if not connection_check_on_start and num_top_proxies is not None:
            print("'num_top_proxies' is set to yet 'check_on_start' is not True."
                  "This means that pool size will be reduced to num_top_proxies per proxy type, yet it's not "
                  "guaranteed that those proxies are with the best connection out of all provided proxies.")

        self.__pool = PriorityQueue()
        self.__test_url = test_url
        self.__fail_predicate_fn = fail_predicate_fn
        self.__verbose = verbose

        self.__l_http = list(set(l_http))
        self.__l_https = list(set(l_https))
        self.__l_sock4 = list(set(l_sock4))
        self.__l_sock5 = list(set(l_sock5))

        self.__timeout = timeout
        self.__index = 0

        self.__update_lock = RLock()

        self.__init_pool(connection_check_on_start, num_top_proxies)

    def __init_pool(self, check, num_top_proxies):
        print("initializing proxy pool...")
        print("http: {}, https: {}, sock4: {}, sock5: {}".format(len(self.__l_http),
                                                                 len(self.__l_https),
                                                                 len(self.__l_sock4),
                                                                 len(self.__l_sock5)))
        self.__process_list(self.__l_http, "http", check, num_top_proxies)
        self.__process_list(self.__l_https, "https", check, num_top_proxies)
        self.__process_list(self.__l_sock4, "socks4", check, num_top_proxies)
        self.__process_list(self.__l_sock5, "socks5", check, num_top_proxies)

        self.__pool_size = self.__pool.qsize()

        print("Done! Pool size [{}]".format(self.__pool_size))

    def __process_list(self, in_list, type, check, num_top_proxies):
        host_list = in_list.copy()
        size = len(host_list)

        results = []
        with ThreadPoolExecutor() as exec:
            if check:
                duration_list = exec.map(lambda host: self.get_duration(type, host), host_list)
                duration_list = zip(duration_list, host_list)  # (duration, host)
                host_list = filter(lambda tup: tup[0] <= self.__timeout, duration_list)
            else:
                host_list = list(zip([999.0 for _ in range(len(host_list))], host_list))
            result = map(lambda tup: ProxyInfo(self, tup[1].rstrip('\n'), type, tup[0]), host_list)

            for i, result_each in enumerate(result):
                sys.stdout.write("\rProgression for {0} = {1:.2f}%".format(type, (i / size) * 100))
                sys.stdout.flush()
                results.append(result_each)
            sys.stdout.write("\rProgression for {0} = {1:.2f}%\n".format(type, 100.0))

        if num_top_proxies:
            results.sort()
            results = results[:num_top_proxies]

        for result in results:
            self.__pool.put(result)

        in_list.clear()
        in_list.extend(map(lambda host_info: host_info.get_host(), results))

        print("list of {} proxies are ready. Size: {}".format(type, len(in_list)))

    def get_duration(self, type, host):
        proxy_type = type.rstrip()
        proxy_host = host.rstrip()

        start = time.time()
        duration = 999.0
        try:
            formatted_host = "{}://{}".format(proxy_type, proxy_host)
            result = requests.session().get(self.__test_url,
                                            headers={'User-Agent': get_random_useragent()},
                                            proxies={PROTOCOL: formatted_host},
                                            timeout=self.__timeout,
                                            stream=True)
            if not self.__fail_predicate_fn(result):
                raise Exception("Predicate failed {}".format(result))
            duration = time.time() - start
        except Exception as ex:
            if self.__verbose:
                print("proxy host {} is invalid. Cause: {}".format(proxy_host, ex))

            duration = 999
            pass
        finally:
            return duration

    # def __async_sort(self):
    #     if self.__cycle_proxy:
    #         return # don't sort. we will just cycle proxy in order
    #
    #     def sort(pool):
    #         with self.__sorting_lock:
    #             try:
    #                 with self.__update_lock:
    #                     start = time.time()
    #                     pool.sort()
    #             finally:
    #                 self.__sorting = False
    #
    #                 if self.__verbose:
    #                     print("sorted {}s".format(time.time() - start))
    #
    #     if not self.__sorting:
    #         self.__sorting = True
    #         self.__sorting_thread_pool.submit(sort, self.__pool)

    # def notify(self, observable):
    #     self.__async_sort()
    #
    # def __run(self):
    #     while True:
    #         time.sleep(1)
    #         self.__async_sort()

    def get_proxy(self):
        """
        Get currently available ProxyInfo.

        Best Practice:
            with my_pool.get_proxy() as proxy_info:
                response = requests.get(my_url, proxies=proxy_info.request_style_proxies_dict(PROTOCOL))
                # you may manually update the response time, so it can be reordered
                proxy_info.set_response_time(new_response_time)
        :return: ProxyInfo
            the ProxyInfo instance which is available to be used.
        """
        # reuse index if cycling

        while True:
            with self.__update_lock:
                if self.__pool.empty():
                    print("Proxy pool is empty. Wait for 3 seconds and will retry...")
                    time.sleep(3)
                    continue

                proxy_info = self.__pool.get(True)

                duration = self.get_duration(proxy_info.get_type(), proxy_info.get_host())
                proxy_info.set_response_time(duration)
                if duration > self.__timeout:
                    if self.__verbose:
                        print("Proxy Timeout: {}".format(proxy_info))
                    continue

                if self.__verbose:
                    print("Proxy acquired: {}".format(proxy_info))

                return proxy_info

        return None

    def notify(self, observable):
        with self.__update_lock:
            self.__pool.put(observable)


def build_proxy_dict(folder="proxies", txt_file_names=None):
    """
    Build simple proxy dictionary from the given folder. The folder can contain the following
    files: http.txt, https.txt, socks4.txt, and socks5.txt.

    Each file must present one proxy server per line, and each line should follow ip:port format.

    :param folder: folder to search for the proxy files
    :param txt_file_names: file names. http.txt, https.txt, socks4.txt, and socks5.txt by default
    :return: dictionary of proxy server list.
    """
    if txt_file_names is None:
        txt_file_names = ["http", "https", "socks4", "socks5"]

    proxy_list_dict = {}
    for file in txt_file_names:
        path = os.path.join(folder, file + ".txt")
        if not os.path.exists(path):
            continue

        print("Path: {}".format(path))

        with open(path) as f:
            proxy_list = f.readlines()
        proxy_list_dict[file] = list(map(lambda elem: elem.rstrip('\n'), set(proxy_list)))
    return proxy_list_dict


def build_proxy_pool(test_url,
                     proxy_list_dict,
                     pred,
                     timeout=2,
                     check_on_start=True,
                     num_top_proxies=100,
                     verbose=False):
    return ProxyPool(test_url,
                     proxy_list_dict['http'],
                     proxy_list_dict['https'],
                     proxy_list_dict['socks4'],
                     proxy_list_dict['socks5'],
                     pred,
                     timeout=timeout,
                     connection_check_on_start=check_on_start,
                     num_top_proxies=num_top_proxies,
                     verbose=verbose)
