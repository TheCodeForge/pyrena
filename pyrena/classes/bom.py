from .base import *

class BOM(Object):
    endpoint="/items/{guid}/bom"

    @cachedproperty
    def settings(self):
        return self._client.get(f"/items{self.guid}/bom/settings")

    @cachedproperty
    def lines(self):

        lines=[self._client.BOMLine(**dataset) for dataset in self.results]
        for line in lines:
            line.bom=self


class BOMLine(Object):

    @cachedproperty
    def endpoint(self):
        return f"/items/{self.bom.guid}/bom/{self.guid}"
    
    @cachedproperty
    def item(self):
        return self._client.Item(self.__dict__["item"]["guid"])