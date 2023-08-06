import logging
from typing import List, Optional
from warnings import warn

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.nds_aggregates import NdsAggregateList, NdsAggregateRowList
from cognite.well_model.client.models.property_filter import PropertyFilter, filter_to_model
from cognite.well_model.client.models.resource_list import NdsList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DeleteEventSources,
    DistanceRange,
    EventExternalId,
    Nds,
    NdsAggregateEnum,
    NdsAggregateItems,
    NdsAggregateRequest,
    NdsAggregateRequestFilter,
    NdsFilter,
    NdsFilterRequest,
    NdsIngestion,
    NdsIngestionItems,
    NdsItems,
)

logger = logging.getLogger(__name__)


def _validate_deprecated_fields(ingestion: NdsIngestion):
    if ingestion.hole_start is not None:
        warn(DeprecationWarning("NdsIngestion.hole_start is deprecated. Use hole_top instead."))
        if ingestion.hole_top is None:
            ingestion.hole_top = ingestion.hole_start
        else:
            warn(UserWarning("NdsIngestion both hole_start and hole_top are present, hole_start is ignored"))
        ingestion.hole_start = None

    if ingestion.hole_end is not None:
        warn(DeprecationWarning("NdsIngestion.hole_end is deprecated. Use hole_base instead."))
        if ingestion.hole_base is None:
            ingestion.hole_base = ingestion.hole_end
        else:
            warn(UserWarning("NdsIngestion both hole_end and hole_base are present, hole_end is ignored"))
        ingestion.hole_end = None
    return ingestion


class NdsEventsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, nds_events: List[NdsIngestion]) -> NdsList:
        """Ingest NDS events

        Args:
            nds_events (List[NdsIngestion]): list of Nds events to ingest
        Returns:
            NdsList:
        Warning:
            NdsIngestion.hole_start is deprecated, use hole_top instead.

            NdsIngestion.hole_end is deprecated, use hole_base instead.
        """
        nds_events = [_validate_deprecated_fields(ingestion) for ingestion in nds_events]

        if len(nds_events) == 0:
            return NdsList([])
        path = self._get_path("/nds")
        json = NdsIngestionItems(items=nds_events).json()
        response: Response = self.client.post(path, json)
        return NdsList(NdsItems.parse_raw(response.text).items)

    def list(
        self,
        hole_start: Optional[DistanceRange] = None,
        hole_end: Optional[DistanceRange] = None,
        hole_top: Optional[DistanceRange] = None,
        hole_base: Optional[DistanceRange] = None,
        probabilities: Optional[List[int]] = None,
        severities: Optional[List[int]] = None,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        risk_types: PropertyFilter = None,
        subtypes: PropertyFilter = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> NdsList:
        """Get Nds events that matches the filter

        Args:
            hole_start: Deprecated, use hole_top
            hole_top: range of hole top in desired Nds events
            hole_end: Deprecated, use hole_base
            hole_base: range of base end in desired Nds events
            probabilities: list of interested probabilities
            severities: list of interested severities
            wellbore_asset_external_ids: list of wellbore asset external ids
            wellbore_matching_ids: list of wellbore matching ids
            limit: optional limit. Set to None to get everything
        Returns:
            NdsList:
        Warning:
            hole_start is deprecated, use hole_top instead.

            hole_end is deprecated, use hole_base instead.
        """
        if hole_start is not None:
            warn(DeprecationWarning("client.nds_events.list hole_start is deprecated use hole_top"))
            if hole_top is None:
                hole_top = hole_start
            else:
                warn(
                    UserWarning(
                        "client.nds_events.list both hole_start and hole_top are present, hole_start is ignored"
                    )
                )
        if hole_end is not None:
            warn(DeprecationWarning("client.nds_events.list hole_end is deprecated use hole_base"))
            if hole_base is None:
                hole_base = hole_end
            else:
                warn(UserWarning("client.nds_events.list both hole_end and hole_base are present, hole_end is ignored"))

        def request(cursor, limit):
            nds_filter = NdsFilterRequest(
                filter=NdsFilter(
                    hole_top=hole_top,
                    hole_base=hole_base,
                    probabilities=probabilities,
                    severities=severities,
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                    risk_type=filter_to_model(risk_types),
                    subtype=filter_to_model(subtypes),
                ),
                cursor=cursor,
                limit=limit,
            )

            path: str = self._get_path("/nds/list")
            response: Response = self.client.post(url_path=path, json=nds_filter.json())
            nds_items: NdsItems = NdsItems.parse_raw(response.text)
            return nds_items

        items = cursor_multi_request(
            get_cursor=self._get_cursor, get_items=self._get_items, limit=limit, request=request
        )
        return NdsList(items)

    def delete(self, event_external_ids: List[str]) -> List[str]:
        """Delete NPT events

        Args:
            event_external_ids (List[str]): List of external ids for NDS events

        Returns:
            List[str]: List of external ids for deleted NDS events
        """
        body = DeleteEventSources(items=[EventExternalId(event_external_id=id) for id in event_external_ids])
        path: str = self._get_path("/nds/delete")
        response: Response = self.client.post(url_path=path, json=body.json())
        response_parsed: DeleteEventSources = DeleteEventSources.parse_raw(response.text)
        response_nds_external_ids: List[str] = [e.event_external_id for e in response_parsed.items]
        return response_nds_external_ids

    @staticmethod
    def _get_items(nds_items: NdsItems) -> List[Nds]:
        items: List[Nds] = nds_items.items  # For mypy
        return items

    @staticmethod
    def _get_cursor(nds_items: NdsItems) -> Optional[str]:
        next_cursor: Optional[str] = nds_items.next_cursor  # For mypy
        return next_cursor

    def aggregate(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        group_by: List[NdsAggregateEnum] = [],
    ) -> NdsAggregateList:
        """Aggregate NDS events for a list of wellbores

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional): List of wellbore asset external ids
            wellbore_matching_ids (Optional[List[str]], optional): List of wellbore matching ids.
            group_by (List[NdsAggregateEnum], optional): List of aggregation types.
                Allowed values: severity, probability, risk type, subtype.

        Returns:
            NdsAggregateList: List of NDS aggregations

        Examples:
            Aggregate NDS events over severity:
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> aggregates = wm.nds.aggregate(
                ...     group_by=["severity"],
                ...     wellbore_matching_ids=["13/10-F-11 T2"]
                ... )
                >>> aggregates.to_pandas()
                  wellboreMatchingId  count
                0      13/10-F-11 T2      3
                >>> aggregates[0].to_pandas()
                  wellboreMatchingId  count  severity
                0      13/10-F-11 T2      1         3
                1      13/10-F-11 T2      2         5




        """
        path: str = self._get_path("/nds/aggregate")
        request_body = NdsAggregateRequest(
            filter=NdsAggregateRequestFilter(
                wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
            ),
            group_by=group_by,
        )
        response: Response = self.client.post(url_path=path, json=request_body.json())
        aggregate_items = NdsAggregateItems.parse_raw(response.text)
        nds_aggregates = []
        for item in aggregate_items.items:
            nds_aggregates.append(NdsAggregateRowList(item.items, item.wellbore_matching_id))

        return NdsAggregateList(nds_aggregates)
