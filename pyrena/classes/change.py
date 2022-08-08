from .base import *

class Change(Object, openable_mixin):
    listing_endpoint="/changes"
    endpoint="/changes/{guid}"

    @property
    @lazy
    def file_associations(self):
        assocs = self._client.Listing(self._client.ChangeFileAssociation, endpoint=f"/changes/{self.guid}/files")
        for assoc in assocs:
            assoc.change=self
        return assocs

    def add_file(self, file_obj):

        """
        Add File connection to Change.

        Args:

        * file_obj - A File object
        """

        data={
            "file":{
                "guid":file_obj.guid
            }
        }
        x=self._client._post(f"/changes/{self.guid}/files", data=data)

        return self._client.ChangeFileAssociation(x.json())

    @property
    @lazy
    def item_associations(self):
        assocs = self._client.Listing(self._client.ChangeItemAssociation, endpoint=f"/changes/{self.guid}/items")
        for assoc in assocs:
            assoc.change=self
        return assocs

    @property
    @lazy
    def implementation_file_associations(self):

        files = self._client.Listing(self._client.ImplementationFileAssociation, endpoint=f"/changes/{self.guid}/implementationfiles")
        for file in files:
            file.change=self
        return files


    def add_item(self, item_obj, lifecycle_phase=None, new_rev=None):

        """
        Add Item revision to Change.

        Args:

        * item_obj - An Item object. The working revision will be selected.

        Kwargs:

        * lifecycle_phase - An ItemLifecyclePhase object. Defaults to `item_obj.lifecycle_phase` if not specified
        """

        if not lifecycle_phase:
            lifecycle_phase = item_obj.lifecycle_phase

        if lifecycle_phase.stage=='PRELIMINARY':
            raise ValueError("Must specify a DESIGN or PRODUCTION lifecycle phase")

        data={
            "filesView":{
                "includedInThisChange":True,
                "notes":f"Add {item_obj.name}"
            },
            "sourcingView":{
                "includedInThisChange":True,
                "notes":f"Add {item_obj.name}"
            },
            "specsView":{
                "includedInThisChange":True,
                "notes":f"Add {item_obj.name}"
            },
            "bomView":{
                "includedInThisChange":True,
                "notes":f"Add {item_obj.name}"
            },
            "newRevisionNumber": new_rev,
            "newItemRevision":{
                "guid":item_obj.working_revision.guid
            },
            "newLifecyclePhase":{
                "guid": lifecycle_phase.guid
            }
        }
        self._client._post(f"/changes/{self.guid}/items", data=data)

class ChangeFileAssociation(Object):
    
    @property
    @lazy
    def file(self):
        return self._client.File(self.__dict__['file']['guid'])

    @property
    def endpoint(self):
        return f"/changes/{self.change.guid}/files/{self.guid}"

class ChangeItemAssociation(Object):
    
    @property
    @lazy
    def item(self):
        return self._client.Item(self.__dict__['item']['guid'])

    @property
    def endpoint(self):
        return f"/changes/{self.change.guid}/files/{self.guid}"


class ImplementationFileAssociation(Object):

    @property
    def endpoint(self):
        return f"/changes/{self.change.guid}/files/{self.guid}"

    @property
    @lazy
    def file(self):
        return self._client.File(self.__dict__['file']['guid'])
    
class ChangeCategory(Object):

    listing_endpoint="/settings/changes/categories"
    endpoint=listing_endpoint+"/{guid}"
    _can_paginate=False

class ChangeAttribute(Object):

    listing_endpoint="/settings/changes/attributes"
