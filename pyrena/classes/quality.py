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

    def new(self, title, description=None, owner=None, number_format=None, prefix=None):

        """
        Create a new Quality record from this template.

        Required arguments:

        - title     - The title of the new quality record

        Optional arguments:

        - description       - The description of the new record
        - owner             - a User object representing the owner of the new record. Defaults to the authenticated User if not specified.
        - number_format     - a NumberFormat object representing the numbering sequence to use. Defaults to the Template's assigned default sequence (if any) if not specified.
        - prefix            - a string to specify which numbering prefix to use. Required if the number format has more than one prefix option.

        Returns: QualityProcess object
        """

        if not self.active:
            raise RuntimeError(f"Cannot create new instance of inactive Quality Process Template `{self.name}`.")

        number_format = number_format or self.default_number_format

        if len(number_format.prefixes)>1 and not prefix:
            raise ValueError(f"Selected number format has multiple prefixes. Add a `prefix` argument with one of the following values: `{'`, `'.join([x['value'] for x in number_format.prefixes])}`")
        elif len(number_format.prefixes)>1:
            prefix_dict = {x["value"]: x["guid"] for x in number_format.prefixes}
            if prefix not in prefix_dict:
                raise ValueError(f"`prefix` must be one of the following for this numbering format: `{'`, `'.join([x['value'] for x in number_format.prefixes])}`")
            prefix_id=prefix_dict[prefix]
        else:
            prefix_id=number_format.prefixes[0]["guid"]


        data = {  
           "name":title,
           "owner":{  
              "guid": owner.guid if owner else self._client.me.guid
           },
           "template":{  
              "guid": self.guid,
              "numberFormat":{  
                 "prefix":{  
                    "guid": prefix_id
                 }
              }
           }
        }
        if description:
            data["description"]=description

        new_qp = self._client.QualityProcess(**data)
        new_qp.create()
        return new_qp



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