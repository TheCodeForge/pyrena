from base import *

class TrainingPlan(Object):
    listing_endpoint = "/trainingplans"
    endpoint=listing_endpoint+"/{guid}"

    @property
    @lazy
    def manager(self):
        return self._client.User(self.manager['guid'])

    def set_status(self, status):

        """
        Change the Training Plan status.

        Required argument:

        - status - either "OPEN" or "CLOSED"
        """

        if status not in ['OPEN', 'CLOSED']:

            raise ValueError("`status` must be one of \"OPEN\" or \"CLOSED\".")

        body={
            "trainingplan": {
                "guid":self.guid
            },
            "status": status,
        }

        x=self._client._post("/trainingplans/statuschanges", data=body)

        self.__dict__.update(x.json())

    @property
    @lazy
    def item_associations(self):
        assocs = self._client.Listing(self._client.TrainingPlanItem, endpoint=f"/trainingplans/{self.guid}/items")
        for assoc in assocs:
            assoc.change=self
        return assocs

class TrainingPlanItem(Object):
    
    @property
    @lazy
    def item(self):
        return self._client.Item(self.__dict__['item']['guid'])

    @property
    def endpoint(self):
        return f"/trainingplans/{self.ticket.guid}/items/{self.guid}"