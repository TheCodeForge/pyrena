from .base import *

class TrainingPlan(Object):
    listing_endpoint = "/trainingplans"
    endpoint=listing_endpoint+"/{guid}"

    @property
    @lazy
    def manager(self):
        return self._client.User(self.__dict__['manager']['guid'])

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
            assoc.training_plan=self
        return assocs

    @property
    @lazy
    def user_associations(self):
        assocs = self._client.Listing(self._client.TrainingPlanUser, endpoint=f"/trainingplans/{self.guid}/users")
        for assoc in assocs:
            assoc.training_plan=self
        return assocs

    @property
    @lazy
    def records(self):
        recs = self._client.Listing(self._client.TrainingPlanRecord, endpoint=f"/trainingplans/{self.guid}/records")
        for rec in recs:
            rec.training_plan=self
        return recs

    def add_item(self, item):

        """
        Add Item to the training plan

        Required argument:

        - item      - an Item object

        Returns: TrainingPlanItem object
        """

        data={
            "item": {
                "guid": item.guid
            }
        }

        response=self._client._post(f"/trainingplans/{self.guid}/items", data=data)

        i= self._client.TrainingPlanItem(**response)
        i.training_plan=self
        return i

    def add_user(self, user):

        """
        Add User to the training plan

        Required argument:

        - user      - a User object

        Returns: TrainingPlanUser object
        """

        data={
            "user": {
                "guid": user.guid
            }
        }

        response=self._client._post(f"/trainingplans/{self.guid}/users", data=data)

        i= self._client.TrainingPlanUser(**response)
        i.training_plan=self
        return i


class TrainingPlanItem(Object):

    @property
    @lazy
    def item(self):
        return self._client.Item(self.__dict__['item']['guid'])

    @property
    def endpoint(self):
        return f"/trainingplans/{self.training_plan.guid}/items/{self.guid}"

class TrainingPlanUser(Object):
    
    @property
    @lazy
    def user(self):
        return self._client.User(self.__dict__['user']['guid'])

    @property
    def endpoint(self):
        return f"/trainingplans/{self.training_plan.guid}/users/{self.guid}"

class TrainingPlanRecord(Object):

    _can_paginate=False

    @property
    def endpoint(self):
        return f"/trainingplans/{self.training_plan.guid}/records/{self.guid}"

    @property
    @lazy
    def item(self):
        return self._client.Item(self.__dict__['item']['guid'])
    
