import prometheus_client


class Gauge:
    child: prometheus_client.Gauge

    def __init__(self, c: prometheus_client.Gauge, labels: list[str]) -> None:
        self.child = c.labels(*labels)

    def inc(self) -> None:
        self.child.inc()

    def dec(self) -> None:
        self.child.dec()

    def set(self, value: float) -> None:
        self.child.set(value)
