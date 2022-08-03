from .base import *

class Integration(Object):

    listing_endpoint="/outboundintegrations"
    endpoint=listing_endpoint+"/{guid}"

    @property
    @lazy
    def administrators(self):
        data = self._client._get("/outboundintegrations/{self.guid}/administrators")
        return [self._client.User(guid=x) for x in [entry["guid"] for entry in data["results"]]]

    @property
    @lazy
    def events(self):
        events = self._client.Listing(self._client.Event, endpoint=f"/outboundintegrations/{self.guid}/events")
        for event in events:
            event.integration = self
        return events


class Event(Object):

    @property
    def endpoint(self):
        return self.integration.endpoint+f"/events/{self.guid}"

    @property
    @lazy
    def items(self):
        items = self._client.Listing(self._client.EventItem, endpoint=f"{self.endpoint}/items")
        for item in items:
            item.event = self
        return items

    def reconcile(self):
        """
        Mark all Items associated with this event as reconciled.
        """

        return self._client._put(self.endpoint, data={"itemsReconciled":True})

    def unreconcile(self):
        """
        Mark all Items associated with this event as not reconciled.
        """

        return self._client._put(self.endpoint, data={"itemsReconciled":False})


    @property
    @lazy
    def change(self):
        return self._client.Change(guid=self.change["guid"])

    def item_ids(self, reconciled="any"):

        """
        Get IDs of Items associated with this Event.

        Kwargs:

        * reconciled - one of `"true"`, `"false"`, or `"any"`
        """
        
        if reconciled not in ["true", "false", "any"]:
            raise ValueError('`reconciled` must be one of `"true"`, `"false"`, or `"any"`')

        url=f"{self.endpoint}/itemguids"

        data=self._client._get(url, params={"reconciled":reconciled})

        return data["results"]



class EventItem(Object):

    @property
    def endpoint(self):
        return f"/outboundintegrations/{self.event.integration.guid}/events/{self.event.guid}/items/{self.guid}"

    def reconcile(self):
        """
        Mark this event item as reconciled.
        """

        return self._client._put(self.endpoint, data={"reconciled":True})

    def unreconcile(self):
        """
        Mark this event item as not reconciled.
        """

        return self._client._put(self.endpoint, data={"reconciled":False})

    @property
    @lazy
    def item(self):

        return self._client.Item(guid=self.effectiveItemRevision["guid"])

class Trigger(Object):

    listing_endpoint="/settings/integrations/triggers"
    endpoint=listing_endpoint+"/{guid}"
