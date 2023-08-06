from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Warranty_Registrations(Consumer):
    """Inteface to warranty registrations resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("warranties/registrations/")
    def list(
        self,
    ):
        """This call will return warranty registration information for the specified criteria."""

    @returns.json
    @http_get("warranties/registrations/{uid}")
    def get(
        self,
        uid: str
    ):
        """This call will return warranty registration information for the specified criteria."""

    @returns.json
    @delete("warranties/registrations/{uid}")
    def delete(self, uid: str):
        """This call will delete the warranty registration information for the specified uid."""

    @returns.json
    @json
    @post("warranties/registrations/{company_uid}")
    def insert(self, warranty_registration: Body, company_uid: str):
        """This call will create warranty registration information with the specified parameters."""

    @returns.json
    @json
    @patch("warranties/registrations/{uid}")
    def update(self, warranty_registration: Body, uid: str):
        """This call will update the warranty registration information with the specified parameters."""