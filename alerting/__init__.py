from typing import TypeVar, List


class AlertingClient:

    def __init__(self):
        pass

    def send_alert(self, message: str):
        raise NotImplementedError


T = TypeVar('T', bound=AlertingClient)


class Alerting:

    def __init__(self, clients: List[T]):
        assert clients is not None, 'Null clients passed for alerting'
        assert isinstance(clients, list), 'Clients must be a list of "AlertingClient"s instead of ' + str(type(clients))
        for client in clients:
            assert isinstance(client, AlertingClient), 'Client must be a AlertingClient object instead of ' + str(type(client))
        self.clients = clients  # type: List[T]

    def send_alert(self, message: str):
        assert message is not None, 'Null message passed for sending alert'
        assert isinstance(message, str), 'Invalid message type, found ' + str(type(message)) + ' instead of str'
        for client in self.clients:
            client.send_alert(message)

