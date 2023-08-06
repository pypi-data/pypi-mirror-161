from typing import Any

from punch_api.dag import Out


class InputDatasets(dict[str, object]):
    """InputDatasets is used in the execute method of our AbstractNode
    This class gives access to data streams of each node this node is subscribed to
    """

    def get_first(self) -> Any:
        """Get the 'first' dataset (the order is arbitrary due to the map nature)"""
        return self[list(self.keys())[0]]

    def put(self, key: str, value: Any) -> None:
        self[key] = value


class OutputDatasets(dict[Out, object]):
    __outs: list[Out]

    def __init__(self, outs: list[Out]) -> None:
        super().__init__()
        self.__outs = outs

    def put(self, value: Any) -> None:
        """Publish the provided dataset in all the 'out' node configured.

        :param value: the value to publish
        """
        o: Out
        for o in self.__outs:
            self[o] = value
