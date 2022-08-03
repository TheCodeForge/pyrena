from .base import *

class Supplier(Object):
    listing_endpoint="/suppliers"
    endpoint="/suppliers/{guid}"

    @property
    @lazy
    def addresses(self):
        addresses= self._client.Listing(self._client.SupplierAddress, endpoint=f"/suppliers/{self.guid}/addresses")
        for address in addresses:
            address.supplier=self

        return addresses

    @property
    @lazy
    def phones(self):
        phones= self._client.Listing(self._client.SupplierPhone, endpoint=f"/suppliers/{self.guid}/phonenumbers")
        for phone in phones:
            phone.supplier=self

        return phones

    @property
    @lazy
    def quality_processes(self):
        return self._client.Listing(self._client.QualityProcess, endpoint=f"/suppliers/{self.guid}/quality")

    @property
    @lazy
    def files(self):
        files=self._client.Listing(self._client.SupplierFileAssociation, endpoint=f"/suppliers/{self.guid}/files")

        for file in files:
            file.supplier=self

        return files

class SupplierAddress(Object):

    @property
    def listing_endpoint(self):
        return f"/suppliers/{self.supplier.guid}/addresses"
    
    
    @property
    def endpoint(self):
        return f"{self.listing_endpoint}/{self.guid}"

class SupplierFileAssociation(Object):

    @property
    def listing_endpoint(self):
        return f"/suppliers/{self.supplier.guid}/files"

    @property
    def endpoint(self):
        return f"{self.listing_endpoint}/{self.guid}"

    @property
    @lazy
    def file(self):
        return self._client.File(self.__dict__["file"]["guid"])

class SupplierPhone(Object):

    @property
    def listing_endpoint(self):
        return f"/suppliers/{self.supplier.guid}/phonenumbers"
    
    
    @property
    def endpoint(self):
        return f"{self.listing_endpoint}/{self.guid}"