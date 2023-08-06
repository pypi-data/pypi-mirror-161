import os

from typing import Dict, List

from simple_proxy2.data.proxy_info import ProxyInfo


def build_proxy_dict(folder="proxies", txt_file_names=None) -> Dict[str, List[str]]:
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
        proxy_list_dict[file] = list(
            map(lambda elem: elem.rstrip('\n'), set(proxy_list)))
    return proxy_list_dict


def proxy_dict_to_info_list(proxy_dict: Dict[str, List[str]]) -> List[ProxyInfo]:
    info_set = set()

    for protocol, addresses in proxy_dict.items():
        for address in addresses:
            info_set.add(ProxyInfo(protocol, address))

    return list(info_set)
