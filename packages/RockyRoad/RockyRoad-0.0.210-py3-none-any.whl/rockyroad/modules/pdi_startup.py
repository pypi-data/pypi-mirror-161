from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class PDI_Startup(Consumer):
    """Inteface to PDI/Startup resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def reports(self):
        return self.__Reports(self)
    # def forms(self):
    #     return self.__Forms(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Reports(Consumer):
        """Inteface to PDI Startup Reports resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("pdi-startup/reports")
        def list(
        ):
            """This call will return all the pdi/startup reports."""

        @returns.json
        @json
        @post("pdi-startup/reports")
        def insert(self, reports: Body):
            """This call will create an pdi/startup report with the specified parameters."""

        @returns.json
        @http_get("pdi-startup/reports/current/dealer/{dealer_uid}")
        def get_all_for_dealer(self,
            dealer_uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @http_get("pdi-startup/reports/dictionary/machine/{machine_uid}")
        def get_report_with_dictionary_by_machine(self,
            machine_uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @http_get("pdi-startup/reports/dictionary/{uid}")
        def get_report_with_dictionary(self,
            uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @http_get("pdi-startup/reports/machine/{machine_uid}/exists")
        def report_exists_for_machine(self,
            machine_uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @http_get("pdi-startup/reports/machine/{machine_uid}")
        def get_report_by_machine(self,
            machine_uid: str
        ):
            """This call will return detailed report information for the specified criteria."""
        @returns.json
        @http_get("pdi-startup/reports/current/dealer/{uid}")
        def get_report(self,
            uid: str
        ):
            """This call will return detailed report information for the specified criteria."""

        @returns.json
        @delete("pdi-startup/reports/{uid}")
        def delete(self, uid: str):
        """This call will delete specified info for the specified uid."""

        @returns.json
        @json
        @patch("pdi-startup/reports/{uid}")
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

       
