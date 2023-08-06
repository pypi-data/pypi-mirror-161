from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class EDAP(Consumer):
    """Inteface to EDAP resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def asset_sales(self):
        return self.__Asset_Sales(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Asset_Sales(Consumer):
        """Inteface to EDAP Sales resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("edap/sales")
        def list(
            self,
            business_unit_id: Query(type=str) = None,
            model: Query(type=str) = None,
            serial_number: Query(type=str) = None,
        ):
            """This call will return EDAP asset sales information for the specified criteria."""
