from .base import *

class BOM(Object):
    endpoint="/items/{guid}/bom"

    @property
    @lazy
    def settings(self):
        return self._client.get(f"/items{self.guid}/bom/settings")

    @property
    @lazy
    def lines(self):

        lines=[self._client.BOMLine(**dataset) for dataset in self.results]
        for line in lines:
            line.bom=self


class BOMLine(Object):

    @property
    @lazy
    def endpoint(self):
        return f"/items/{self.bom.guid}/bom/{self.guid}"
    
    @property
    @lazy
    def item(self):
        return self._client.Item(self.__dict__["item"]["guid"])