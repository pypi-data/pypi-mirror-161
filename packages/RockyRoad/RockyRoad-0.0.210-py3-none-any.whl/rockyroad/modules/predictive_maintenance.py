from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Predictive_Maintenance(Consumer):
    """Inteface to Predictive Maintenance resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("predictive-maintenance/scores")
    def list(self):
        """This call will return list of predictive maintenance scores."""