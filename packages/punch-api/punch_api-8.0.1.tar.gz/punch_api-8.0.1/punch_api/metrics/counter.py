import prometheus_client


class Counter:
    child: prometheus_client.Counter

    def __init__(self, c: prometheus_client.Counter, labels: list[str]) -> None:
        self.child = c.labels(*labels)

    def inc(self) -> None:
        self.child.inc()
