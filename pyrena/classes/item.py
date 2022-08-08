from .base import *

class Item(Object, openable_mixin):
    listing_endpoint="/items"
    endpoint="/items/{guid}"

    @property
    @lazy
    def bom(self):
        return self._client.BOM(self.guid)

    @property
    @lazy
    def category(self):
        return self._client.ItemCategory(self.__dict__["category"]["guid"])

    @property
    @lazy
    def revisions(self):
        return self._client.Listing(self._client.ItemRevision, endpoint=f"/items/{self.guid}/revisions")

    @property
    @lazy
    def quality_processes(self):
        return self._client.Listing(self._client.QualityProcess, endpoint=f"/items/{self.guid}/quality")

    @property
    @lazy
    def where_used(self):
        return self._client.Listing(self._client.Item, endpoint=f"/items/{self.guid}/whereused")

    @property
    @lazy
    def file_associations(self):
        assocs = self._client.Listing(self._client.ItemFileAssociation, endpoint=f"/items/{self.guid}/files")
        for assoc in assocs:
            assoc.item=self
        return assocs

    @property
    @lazy
    def thumbnail(self):

        return self._client._get(f"/items/{self.guid}/image/content")

    @property
    def working_revision(self):
        rev = [x for x in self.revisions if x.status==0]
        if rev:
            return rev[0]
        else:
            return None

    @property
    def effective_revision(self):
        rev = [x for x in self.revisions if x.status==1]
        if rev:
            return rev[0]
        else:
            return None

    @property
    @lazy
    def lifecycle_phase(self):

        return self._client.ItemLifecyclePhase(self.lifecyclePhase['guid'])

class ItemLifecyclePhase(Object):
    listing_endpoint = "/settings/items/lifecyclephases"
    

class ItemCategory(Object):

    listing_endpoint="/settings/items/categories"
    endpoint=listing_endpoint+"/{guid}"
    _can_paginate=False

    @property
    @lazy
    def attributes(self):
        return self._client.Listing(self._client.ItemCategoryAttribute, endpoint=f"/settings/items/categories/{self.guid}/attributes")

class ItemCategoryAttribute(Object):
    pass

class ItemFileAssociation(Object):
    @property
    @lazy
    def file(self):
        return self._client.File(self.__dict__['file']['guid'])

    @property
    def endpoint(self):
        return f"/items/{self.change.guid}/files/{self.guid}"

class ItemRevision(Object, openable_mixin):
    endpoint = "/items/{guid}"