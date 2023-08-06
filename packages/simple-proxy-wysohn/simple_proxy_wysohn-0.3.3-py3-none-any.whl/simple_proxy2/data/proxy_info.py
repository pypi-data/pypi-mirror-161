class ProxyInfo:
    def __init__(self, protocol: str, address: str):
        self._protocol = protocol
        self._address = address

        self._protocol.replace("https", "http")

    def as_requests_dict(self) -> dict:
        formatted_host = "{}://{}".format(self._protocol, self._address)
        return {'https': formatted_host}

    def __repr__(self):
        return '{}://{}'.format(self._protocol, self._address)
