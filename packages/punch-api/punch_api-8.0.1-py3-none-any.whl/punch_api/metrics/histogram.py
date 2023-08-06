import prometheus_client


class Histogram:
    child: prometheus_client.Histogram

    def __init__(self, c: prometheus_client.Histogram, labels: list[str]) -> None:
        self.child = c.labels(*labels)

    def observe(self, o: float) -> None:
        self.child.observe(o)

    def time(self) -> prometheus_client.context_managers.Timer:
        return self.child.time()
