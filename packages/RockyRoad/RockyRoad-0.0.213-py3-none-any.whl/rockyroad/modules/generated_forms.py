from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Generated_Forms(Consumer):
    """Inteface to generated forms resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def results(self):
        return self.__Results(self)
    def forms(self):
        return self.__Forms(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Forms(Consumer):
        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("generated/form/forms/machine/catalog/{machine_catalog_uid}")
        def get_form_by_machine_catalog(self, machine_catalog_uid: str):
            """This call will get a form based on the criteria"""


    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Results(Consumer):
        """Inteface to PDI Startup Results resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("generated/form/results")
        def list(
        ):
            """This call will return all the pdi/startup reports."""

        @returns.json
        @json
        @post("generated/form/results")
        def insert(self, reports: Body):
            """This call will create an pdi/startup report with the specified parameters."""

        @returns.json
        @http_get("generated/form/results/current/dealer/{dealer_uid}")
        def get_all_for_dealer(self,
            dealer_uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @http_get("generated/form/results/dictionary/machine/{machine_uid}")
        def get_report_with_dictionary_by_machine(self,
            machine_uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @http_get("generated/form/results/dictionary/{uid}")
        def get_report_with_dictionary(self,
            uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @http_get("generated/form/results/machine/{machine_uid}/exists")
        def report_exists_for_machine(self,
            machine_uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @http_get("generated/form/results/machine/{machine_uid}")
        def get_report_by_machine(self,
            machine_uid: str
        ):
            """This call will return detailed report information for the specified criteria."""
        @returns.json
        @http_get("generated/form/results/current/dealer/{uid}")
        def get_report(self,
            uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @delete("generated/form/results/{uid}")
        def delete(self, uid: str):
            """This call will delete specified info for the specified uid."""

        @returns.json
        @json
        @patch("generated/form/results/{uid}")
        def update(self, report: Body, uid:str):
            """This call will update the report with the specified parameters."""

        # @returns.json
        # @multipart
        # @post("inspections/uploadfiles")
        # def addFile(self, uid: Query(type=str), file: Part):
        #     """This call will create an inspection report with the specified parameters."""

        # @http_get("inspections/download-files")
        # def downloadFile(
        #     self,
        #     uid: Query(type=str),
        #     filename: Query(type=str),
        # ):
        #     """This call will download the file associated with the inspection report with the specified uid."""

        # @returns.json
        # @http_get("inspections/list-files")
        # def listFiles(
        #     self,
        #     uid: Query(type=str),
        # ):
        #     """This call will return a list of the files associated with the inspection report for the specified uid."""

       
