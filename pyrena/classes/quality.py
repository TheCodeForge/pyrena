from .base import *

class QualityProcess(Object):
    listing_endpoint = "/qualityprocesses"
    endpoint=listing_endpoint+"/{guid}"

    @property
    @lazy
    def template(self):
        return self._client.QualityProcessTemplate(self.__dict__["template"]["guid"])

    @property
    @lazy
    def steps(self):
        steps = self._client.Listing(self._client.QualityProcessStep, endpoint=f"/qualityprocesses/{self.guid}/steps")
        for step in steps:
            step.quality_process = self
        return steps

    @property
    @lazy
    def owner(self):
        return self._client.User(self.__dict__['owner']['guid'])

class QualityProcessNumberFormat(Object):
    listing_endpoint = "/settings/qualityprocesses/numberformats"
    endpoint=listing_endpoint+"/{guid}"

class QualityProcessStep(Object):
  
    @property
    def endpoint(self):
        return f"/qualityprocesses/{self.quality_process.guid}/steps/{self.guid}"

    @property
    @lazy
    def assignees(self):
        return [self._client.User(guid) for guid in [x['guid'] for x in self.__dict__['assignees']['users']]]

    def complete(self, comment=""):

        """
        Mark the Step as Complete.
        """

        data={  
           "Quality Process":{
               "guid":self.quality_process.guid,
               "step": {
                   "guid": self.guid
               }
           },
           "complete":True,
           "comment":comment
        }

        return self.quality_process._client._post(
            self.endpoint,
            data=data
            )
          
    def reopen(self, comment=""):

        """
        Reopen a completed Step.
        """

        data={  
           "Quality Process":{
               "guid":self.quality_process.guid,
               "step": {
                   "guid": self.guid
               }
           },
           "complete":False,
           "comment":comment
        }

        return self.quality_process._client._put(
            f"/qualityprocess/statuschanges",
            data=data
            )

    @property
    @lazy
    def attributes(self):

        #Arena only reports steps with data so let's fill in all from template
        #get the same number step; attributes are thankfully in order
        attrs_list = self.quality_process.template.steps[self.quality_process.steps.index(self)].attributes

        construct 


        attrs = [self._client.QualityProcessAttribute(**kwargs) for kwargs in self.__dict__['attributes']]
        for attr in attrs:
            attr.quality_process_step = self
        return attrs

    def assign(self, user):

        """
        Set the step assignee.

        Required arguments:

        - user    - a User object
        """

        data={
            "assignees":{
                "users":[
                    {
                        "guid": user.guid
                    }
                ]
            }
        }

        return self.quality_process._client._put(
            self.endpoint,
            data=data
            )


class QualityProcessTemplate(Object):
    listing_endpoint="/settings/qualityprocesses/templates"
    endpoint = listing_endpoint+"/{guid}"
    _can_paginate = False

    @property
    @lazy
    def number_formats(self):
        return [self._client.QualityProcessNumberFormat(**dataset) for dataset in  self.__dict__.get("numberFormats", [])]

    @property
    @lazy
    def default_number_format(self):
        return self._client.QualityProcessNumberFormat(self.__dict__['defaultNumberFormat']['guid'])

    @property
    @lazy
    def steps(self):
        steps=[self._client.QualityProcessTemplateStep(**dataset) for dataset in self.__dict__['steps']]
        for step in steps:
            step.template=self

        return steps

    def new(self, title, description=None, owner=None, number_format=None):

        """
        Create a new Quality record from this template.

        Required arguments:

        - title     - The title of the new quality record

        Optional arguments:

        - description       - The description of the new record
        - owner             - a User object representing the owner of the new record. Defaults to the authenticated User if not specified.
        - number_format     - a NumberFormat object representing the numbering sequence to use. Defaults to the Template's assigned default sequence if not specified.

        Returns: QualityProcess object
        """

        {  
           "description":description or "",
           "name":name,
           "owner":{  
              "guid": owner.guid if owner else self._client.me.guid
           },
           "template":{  
              "guid": self.guid,
              "numberFormat":{  
                 "prefix":{  
                    "guid": number_format.guid if number_format else self.__dict__['defaultNumberFormat']['guid'] 
                 }
              }
           },
           "type":""
        }



class QualityProcessTemplateStep(Object):
    pass

class QualityProcessAttribute(Object):
    
    def update(self, value):

        """
        Set the value of the attribute within the quality process.
        """

        data={
            "attributes":[
                {
                    "guid":self.guid,
                    "value": value
                }
            ]
        }

        return self._client._put(
            self.quality_process_step.endpoint,
            data=data
            )