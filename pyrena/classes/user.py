from .base import *

class User(Object):
    listing_endpoint = "/settings/users"
    endpoint=listing_endpoint+"/{guid}"

    @property
    def name(self):
        return self.fullName


class UserGroup(Object):
    listing_endpoint = "/settings/usergroups"
    endpoint=listing_endpoint+"/{guid}"

    @property
    @lazy
    def users(self):

        return self._client.Listing(self._client.User, endpoint=f"/settings/usergroups/{self.guid}/users")
