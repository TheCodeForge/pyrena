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
        return f"/qualityprocess/{self.qualityprocess.guid}/steps/{self.guid}"

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
               "guid":self.qualityprocess.guid,
               "step": {
                   "guid": self.guid
               }
           },
           "complete":True,
           "comment":comment
        }

        return self._client._post(
            f"/qualityprocess/statuschanges",
            data=data
            )
          
    def reopen(self, comment=""):

        """
        Reopen a completed Step.
        """

        data={  
           "Quality Process":{
               "guid":self.qualityprocess.guid,
               "step": {
                   "guid": self.guid
               }
           },
           "complete":False,
           "comment":comment
        }

        return self._client._post(
            f"/qualityprocess/statuschanges",
            data=data
            )  

class QualityProcessTemplate(Object):
    listing_endpoint="/settings/qualityprocesses/templates"
    endpoint = listing_endpoint+"/{guid}"

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
        steps=[self._client.QualityProcessTemplateStep(**dataset) for dataset in self.steps]
        for step in steps:
            step.template=self

class QualityProcessTemplateStep(Object):
    pass

class QualityAttribute(Object):

    listing_endpoint="/settings/quality/attributes"