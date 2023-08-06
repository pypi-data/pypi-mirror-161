from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import MeasurementTypeDetailsList
from cognite.well_model.models import (
    MeasurementTypeDetails,
    MeasurementTypeDetailsItems,
    MeasurementTypeFilter,
    MeasurementTypeFilterRequest,
)


class MeasurementTypesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def list(self, measurement_types: Optional[List[str]] = None) -> MeasurementTypeDetailsList:
        """Get a list of measurement types details

        Args:
            measurement_types (List[str]): List of measurement types to be retrieved.
        Returns:
            List[MeasurementTypeDetails]: A list of measurement type details

        Examples:
            Get measurement types of type "gamma ray" and caliper
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> types = wm.measurement_types.list(["gamma ray", "caliper"])
        """
        if measurement_types is not None and len(measurement_types) == 0:
            return MeasurementTypeDetailsList([])
        path: str = self._get_path("/measurementtypes/list")
        types_filter = None
        if measurement_types is not None:
            types_filter = MeasurementTypeFilter(measurement_types=measurement_types)
        json = MeasurementTypeFilterRequest(filter=types_filter).json()
        response: Response = self.client.post(path, json)
        types_details: List[MeasurementTypeDetails] = MeasurementTypeDetailsItems.parse_raw(response.content).items
        return MeasurementTypeDetailsList(types_details)
