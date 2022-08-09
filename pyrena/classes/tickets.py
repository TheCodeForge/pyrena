from .base import *

class Ticket(Object):
    listing_endpoint = "/tickets"
    endpoint=listing_endpoint+"/{guid}"

    def set_status(self, status):

        """
        Change the Ticket status.

        Required argument:

        - status - one of "NOT_STARTED", "IN_PROGRESS", or "COMPLETE"
        """

        if status not in ['NOT_STARTED', 'IN_PROGRESS', 'COMPLETE']:

            raise ValueError("`status` must be one of \"NOT_STARTED\", \"IN_PROGRESS\", or \"COMPLETE\".")

        body={
            "ticket": {
                "guid":self.guid
            },
            "status": status
        }

        x=self._client._post("/tickets/statuschanges", data=body)

        self.__dict__.update(x.json())


    @property
    @lazy
    def file_associations(self):
        assocs = self._client.Listing(self._client.TicketFileAssociation, endpoint=f"/tickets/{self.guid}/files")
        for assoc in assocs:
            assoc.ticket=self
        return assocs

    @property
    @lazy
    def change_associations(self):
        assocs = self._client.Listing(self._client.TicketChangeAssociation, endpoint=f"/tickets/{self.guid}/changes")
        for assoc in assocs:
            assoc.ticket=self
        return assocs

    @property
    @lazy
    def quality_associations(self):
        assocs = self._client.Listing(self._client.TicketQualityAssociation, endpoint=f"/tickets/{self.guid}/quality")
        for assoc in assocs:
            assoc.ticket=self
        return assocs

    @property
    @lazy
    def ticket_associations(self):
        assocs = self._client.Listing(self._client.TicketTicketAssociation, endpoint=f"/tickets/{self.guid}/tickets")
        for assoc in assocs:
            assoc.ticket=self
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
        x=self._client._post(f"/tickets/{self.guid}/files", data=data)

        return self._client.TicketFileAssociation(x.json())

class TicketFileAssociation(Object):
    
    @property
    @lazy
    def file(self):
        return self._client.File(self.__dict__['file']['guid'])

    @property
    def endpoint(self):
        return f"/tickets/{self.ticket.guid}/files/{self.guid}"

class TicketChangeAssociation(Object):
    @property
    @lazy
    def change(self):
        return self._client.Change(self.__dict__['change']['guid'])

    @property
    def endpoint(self):
        return f"/tickets/{self.ticket.guid}/changes/{self.guid}"

class TicketQualityAssociation(Object):
    
    @property
    @lazy
    def quality(self):
        return self._client.QualityProcess(self.__dict__['quality']['guid'])

    @property
    def endpoint(self):
        return f"/tickets/{self.ticket.guid}/quality/{self.guid}"

class TicketTicketAssociation(Object):
    
    @property
    @lazy
    def other_ticket(self):
        return self._client.Ticket(self.__dict__['ticket']['guid'])

    @property
    def endpoint(self):
        return f"/tickets/{self.ticket.guid}/quality/{self.guid}"

class TicketAttribute(Object):

    listing_endpoint="/settings/tickets/attributes"