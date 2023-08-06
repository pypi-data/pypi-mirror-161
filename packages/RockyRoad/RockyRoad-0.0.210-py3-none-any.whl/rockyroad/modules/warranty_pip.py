from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Product_Improvements(Consumer):
    """Inteface to Warranties Product Improvement resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def populations(self):
        return self.Populations(self)

    def machines(self):
        return self.Machines(self)

    @returns.json
    @http_get("warranties/product-improvements")
    def list(self, is_published: Query(type=bool) = None):
        """This call will return list of product improvements."""

    @delete("warranties/product-improvements/{uid}")
    def delete(self, uid: str):
        """This call will delete the product improvement for the specified uid."""

    @returns.json
    @json
    @post("warranties/product-improvements")
    def insert(self, product_improvement: Body):
        """This call will create the product improvement with the specified parameters."""

    @json
    @patch("warranties/product-improvements/{uid}")
    def update(self, uid: str, product_improvement: Body):
        """This call will update the product improvement with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class Populations(Consumer):
        """Inteface to Warranties Product Improvement Populations resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @delete("warranties/product-improvements/populations/{uid}")
        def delete(self, uid: str):
            """This call will delete the population for the specified uid."""

        @returns.json
        @json
        @post("warranties/product-improvements/{pip_uid}/populations")
        def insert(self, pip_uid: str, population: Body):
            """This call will create the population for the specified product improvement."""

        @json
        @patch("warranties/product-improvements/populations/{uid}")
        def update(self, uid: str, population: Body):
            """This call will update the population with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class Machines(Consumer):
        """Inteface to Warranties PIP machines resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("warranties/product-improvements/machines")
        def list(
            self,
            machine_uid: Query(type=str) = None,
            model: Query(type=str) = None,
            serial: Query(type=str) = None,
        ):
            """This call will return list of PIP machines."""

        @delete("warranties/product-improvements/machines/{uid}")
        def delete(self, uid: str):
            """This call will the PIP machine."""

        @returns.json
        @json
        @post("warranties/product-improvements/{pip_uid}/machines")
        def insert(self, pip_uid: str, pip_machine: Body):
            """This call will create the PIP machine."""

        @json
        @patch("warranties/product-improvements/machines/{uid}")
        def update(self, uid: str, pip_machine: Body):
            """This call will update the PIP machine."""