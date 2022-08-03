from .base import *

class File(Object):
    listing_endpoint="/files"
    endpoint="/files/{guid}"

    @property
    @lazy
    def author(self):
        return self._client.User(self.__dict__['author'])

    def update_file_contents(self, filename):

        """
        Administratively replace this File's document with a new one.

        Required arguments:
        - filename   - Path to the file to upload
        """

        with open(filename, "r+") as file:
            self._client._post(
                f"{self.endpoint}/content",
                files={
                    'content':file
                    }
                )

    def check_out(self, comment="Checking out for review"):
        """
        Checks out the File for edits
        """

        data={
            "checkedOut":True,
            "comment":comment,
            "file":{
                "guid":self.guid
            }
        }
        return self._client._post(
            "/files/checkoutstatuschanges",
            data=data
            )

    def cancel_check_out(self, comment="Cancelling file checkout"):

        """
        Reverts File to "Checked In" state.
        """

        data={
            "checkedOut":False,
            "comment":comment,
            "file":{
                "guid":self.guid
            }
        }
        return self._client._post(
            "/files/checkoutstatuschanges",
            data=data
            )

    def check_in(self, filename, comment="Checking in for update"):

        """
        Upload and check in new version of file to replace existing version.
        """

        with open(filename, "r+") as file:

            files = {
                "file.content":file
            }

            data = {
                "file.guid": self.guid,
                "newEdition":True
            }

            returnval= self._client._post(
                "/files/checkoutstatuschanges",
                data=data,
                files=files
                )

        return returnval

    @property
    @lazy
    def corrections(self):
        return self._client.Listing(self._client.FileCorrection, endpoint=f"/files/{self.guid}/corrections")

    @property
    @lazy
    def editions(self):
        return self._client.Listing(self._client.File, endpoint=f"/files/{self.guid}/editions")

    @property
    @lazy
    def content(self):
        return self._client._get(f"/files/{self.guid}/content").content




class FileCorrection(Object):
    pass


class FileCategory(Object):

    listing_endpoint="/settings/files/categories"
    endpoint=listing_endpoint+"/{guid}"
    _can_paginate=False

class FileAttribute(Object):

    listing_endpoint="/settings/files/attributes"