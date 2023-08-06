import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import HoleSectionGroupsList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DeleteExternalIdSource,
    Distance,
    DistanceRange,
    ExternalIdSource,
    HoleSectionFilter,
    HoleSectionFilterRequest,
    HoleSectionGroupIngestion,
    HoleSectionGroupsIngestionItems,
    HoleSectionGroupsItems,
    TimeRange,
)

logger = logging.getLogger(__name__)


class HoleSectionsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, hole_sections: List[HoleSectionGroupIngestion]) -> HoleSectionGroupsList:
        """Ingest hole sections

        Args:
            hole_sections (List[HoleSectionGroupIngestion]):

        Returns:
            HoleSectionGroupsList:
        """
        if len(hole_sections) == 0:
            return HoleSectionGroupsList([])
        path = self._get_path("/holesections")
        json = HoleSectionGroupsIngestionItems(items=hole_sections).json()
        response: Response = self.client.post(path, json)
        return HoleSectionGroupsList(HoleSectionGroupsItems.parse_raw(response.text).items)

    def list(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        bit_size: Optional[Distance] = None,
        hole_size: Optional[Distance] = None,
        top_measured_depth: Optional[DistanceRange] = None,
        base_measured_depth: Optional[DistanceRange] = None,
        start_time: Optional[TimeRange] = None,
        end_time: Optional[TimeRange] = None,
        is_definitive: Optional[bool] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> HoleSectionGroupsList:
        """List hole sections

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional):
            wellbore_matching_ids (Optional[List[str]], optional):
            limit (Optional[int], optional): Max number of hole section groups to return.
            bit_size (Optional[Distance]): Bit size of a hole section,
            hole_size (Optional[Distance]): Hole size of a hole section,
            top_measured_depth (Optional[DistanceRange]): Shallowest point of a hole sections,
            base_measured_depth (Optional[DistanceRange]): Deepest point of a hole sections,
            start_time (Optional[TimeRange]): Start time for a hole section creation,
            end_time (Optional[TimeRange]): End time for a hole section creation,
            is_definitive (Optional[bool]): Specify if hole sections needs to be marked as definite or not,
                if not specified both definite and not definitive hole sections are returned,

        Returns:
            HoleSectionGroupsList:
        """

        def request(cursor, limit):
            identifiers = identifier_list(wellbore_asset_external_ids, wellbore_matching_ids)
            path = self._get_path("/holesections/list")
            json = HoleSectionFilterRequest(
                filter=HoleSectionFilter(
                    wellbore_ids=identifiers,
                    bit_size=bit_size,
                    hole_size=hole_size,
                    top_measured_depth=top_measured_depth,
                    base_measured_depth=base_measured_depth,
                    start_time=start_time,
                    end_time=end_time,
                    is_definitive=is_definitive,
                ),
                limit=limit,
                cursor=cursor,
            ).json()
            response: Response = self.client.post(path, json)
            hole_section_groups_items = HoleSectionGroupsItems.parse_raw(response.text)
            return hole_section_groups_items

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.items,
            limit=limit,
            request=request,
        )
        return HoleSectionGroupsList(items)

    def delete(self, external_ids: List[str]) -> List[str]:
        """Delete Hole Section Groups

        Args:
            external_ids (List[str]): List of external ids for hole section groups to be deleted

        Returns:
            List[str]: List of external ids for deleted hole section groups.
        """
        body = DeleteExternalIdSource(items=[ExternalIdSource(external_id=external_id) for external_id in external_ids])
        path: str = self._get_path("/holesections/delete")
        response: Response = self.client.post(url_path=path, json=body.json())
        response_parsed: DeleteExternalIdSource = DeleteExternalIdSource.parse_raw(response.text)
        return [s.external_id for s in response_parsed.items]
