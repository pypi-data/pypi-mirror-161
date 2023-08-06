import time

import requests
from requests.sessions import Session

from simple_proxy.proxy_pool import ProxyPool, PROTOCOL, build_proxy_pool
from simple_proxy.user_agents import get_random_useragent


class ProxiedSession(Session):
    def __init__(self, proxy_pool: ProxyPool, fail_predicate_fn, timeout=2, verbose=False):
        super().__init__()
        self.__proxy_pool = proxy_pool
        self.__fail_predicate_fn = fail_predicate_fn
        self.__timeout = timeout
        self.__verbose = verbose

    def request(self, method, url,
                params=None, data=None, headers=None, cookies=None, files=None,
                auth=None, timeout=None, allow_redirects=True, proxies=None,
                hooks=None, stream=True, verify=None, cert=None, json=None):
        retry_limit = 1000
        retries = 0

        f_header = {'User-Agent': get_random_useragent()}
        if headers is not None:
            f_header.update(headers)

        while retries < retry_limit * 2:
            with self.__proxy_pool.get_proxy() as proxy_info:
                if proxy_info is None:
                    retries += 1
                    print("No proxy available. Waiting for 1 second...")
                    time.sleep(1)
                    break

                start = time.time()
                response = None
                try:
                    response = requests.session().request(method, url, params, data, f_header, cookies, files,
                                                          auth,
                                                          self.__timeout if timeout is None else timeout,
                                                          allow_redirects,
                                                          proxy_info.request_style_proxies_dict(PROTOCOL),
                                                          hooks, stream, verify, cert, json)

                    # process stream early here so it doesn't fail later
                    preprocessed_len = len(response.content)
                    if self.__verbose:
                        print("Preprocessed content size: {}".format(preprocessed_len))

                    if not self.__fail_predicate_fn(response):
                        raise Exception("Response {} failed on predicate.".format(response))

                    return response
                except Exception as ex:
                    if self.__verbose:
                        print(ex)
                        print("failure request for {} using {}".format(url, proxy_info))
                        print("will try with another proxy. Retries: {}".format(retries))

                    start = 0 # so response time increase
                    retries += 1
                finally:
                    response_time = time.time() - start
                    if self.__verbose:
                        print("{} New response time: {}".format(proxy_info, response_time))
                    proxy_info.set_response_time(response_time)

                    if response is not None:
                        response.close()

        print("tried {} times but cannot use proxy for {}. Are all proxies dead?".format(retry_limit, url))
        print("continuing with default proxy.")
        return requests.session().request(method, url, params, data, f_header, cookies, files, auth, timeout,
                                          allow_redirects,
                                          proxies,
                                          hooks, stream, verify, cert, json)


def build_proxied_session(test_url, proxy_list_dict, pred, timeout=2, check_on_start=True, num_top_proxies=100,
                          verbose=False):
    """
    create a request Session() which has built-in proxy support.
    :param test_url: str
    :param proxy_list_dict: dict
    :param pred: function
    :param timeout: int
    :param check_on_start: bool
    :param verbose: bool
    :return:
    """
    return ProxiedSession(
        build_proxy_pool(test_url, proxy_list_dict, pred, timeout, check_on_start, num_top_proxies=num_top_proxies,
                         verbose=verbose),
        pred,
        timeout=timeout,
        verbose=verbose)
