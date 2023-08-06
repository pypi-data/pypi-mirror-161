__all__ = [
    "BasicOPCBrowseElement",
    "BrowseElementType",
    "OPCBrowseElement",
    "ServerBrowseElement",
]

from typing import Any, List

from java.lang import Enum, Object


class OPCBrowseElement(object):
    def getDataType(self):
        raise NotImplementedError

    def getDescription(self):
        raise NotImplementedError

    def getDisplayName(self):
        raise NotImplementedError

    def getElementType(self):
        raise NotImplementedError

    def getServerNodeId(self):
        raise NotImplementedError


class BasicOPCBrowseElement(Object, OPCBrowseElement):
    def __init__(self, *args):
        # type: (Any) -> None
        pass

    def getDataType(self):
        pass

    def getDescription(self):
        pass

    def getDisplayName(self):
        pass

    def getElementType(self):
        pass

    def getServerNodeId(self):
        pass


class BrowseElementType(Enum):
    def isSubscribable(self):
        # type: () -> bool
        pass

    @staticmethod
    def values():
        # type: () -> List[BrowseElementType]
        pass


class ServerBrowseElement(Object, OPCBrowseElement):
    _serverName = None

    def __init__(self, serverName):
        self._serverName = serverName

    def getDataType(self):
        pass

    def getDescription(self):
        pass

    def getDisplayName(self):
        pass

    def getElementType(self):
        pass

    def getServerNodeId(self):
        pass
