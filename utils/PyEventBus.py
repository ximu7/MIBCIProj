class PyEventBus(object):
    def __init__(self, ):
        """
        publisher:事件源
        listener:监听者
        event_name:事件id
        """
        self.subscriptions = {}

    def subscribe(self, publisher, event_name, listener, func):
        if listener not in self.subscriptions:
            self.subscriptions[listener] = {}
        if event_name not in self.subscriptions[listener]:
            self.subscriptions[listener][event_name] = {}
        self.subscriptions[listener][event_name][publisher] = func

    def publish(self, publisher, event_name, *args, **kwargs):
        for listener in self.subscriptions.keys():
            if self._has_subscription(publisher, event_name, listener):
                self.subscriptions[listener][event_name][publisher](*args, **kwargs)

    def _has_subscription(self, publisher, event_name, listener):
        return listener in self.subscriptions and \
               event_name in self.subscriptions[listener] and \
               publisher in self.subscriptions[listener][event_name]
