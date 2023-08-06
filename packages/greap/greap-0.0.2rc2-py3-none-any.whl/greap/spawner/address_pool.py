import socket


class AddressPool:
    ...


class LocalAddressPool(AddressPool):
    def create(self, id: str):
        s = socket.socket()
        while True:
            try:
                s.bind(("", 0))  # Bind to a free port provided by the host.
            except Exception:
                pass
            else:
                break
        return f"tcp://0.0.0.0:{s.getsockname()[1]}"


class K8AddressPool(AddressPool):
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace

    def create(self, id: str):
        s = socket.socket()
        while True:
            try:
                s.bind(("", 0))  # Bind to a free port provided by the host.
            except Exception:
                pass
            else:
                break
        # return f"tcp://0.0.0.0:{s.getsockname()[1]}"
        return f"tcp://service-{id}.{self.namespace}.svc.cluster.local:{s.getsockname()[1]}"  # noqa: E501
