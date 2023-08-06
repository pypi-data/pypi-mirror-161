import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import TrajectoryList
from cognite.well_model.client.models.trajectory_rows import TrajectoryRows
from cognite.well_model.client.models.true_vertical_depth_list import TrueVerticalDepthList
from cognite.well_model.client.utils._auxiliary import extend_class
from cognite.well_model.client.utils._distance_unit import create_distance_unit
from cognite.well_model.client.utils._identifier_list import create_identifier, identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DeleteSequenceSources,
    DistanceRange,
    DistanceUnit,
    SequenceExternalId,
    Trajectory,
    TrajectoryData,
    TrajectoryDataRequest,
    TrajectoryFilter,
    TrajectoryFilterRequest,
    TrajectoryIngestion,
    TrajectoryIngestionItems,
    TrajectoryInterpolationRequest,
    TrajectoryInterpolationRequestItems,
    TrajectoryItems,
    TrueVerticalDepths,
)

logger = logging.getLogger(__name__)


class TrajectoriesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

        @extend_class(Trajectory)
        def data(
            this: Trajectory,
            measured_depth: Optional[DistanceRange] = None,
            true_vertical_depth: Optional[DistanceRange] = None,
        ):
            return self.list_data(
                sequence_external_id=this.source.sequence_external_id,
                measured_depth=measured_depth,
                true_vertical_depth=true_vertical_depth,
            )

    def list(
        self,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        is_definitive: Optional[bool] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> TrajectoryList:
        """List trajectories

        Args:
            wellbore_asset_external_ids (Optional[List[str]], optional)
            wellbore_matching_ids (Optional[List[str]], optional)
            is_definitive (Optional[bool], optional): If true, only return
                definitive trajectories. If false, only return non-definitive
                trajectories.
            limit (Optional[int], optional)

        Returns:
            TrajectoryList:

        Examples:
            Retrieve definitive trajectory for a wellbore:
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> trajectories = wm.trajectories.list(
                ...    is_definitive=True,
                ...    wellbore_asset_external_ids=["VOLVE:13/10-F-11 T2"]
                ... )
        """

        def request(cursor, limit):
            filter = TrajectoryFilterRequest(
                filter=TrajectoryFilter(
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                    is_definitive=is_definitive,
                ),
                cursor=cursor,
                limit=limit,
            )

            path: str = self._get_path("/trajectories/list")
            response: Response = self.client.post(url_path=path, json=filter.json())
            trajectory_items: TrajectoryItems = TrajectoryItems.parse_raw(response.text)
            return trajectory_items

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor,
            get_items=lambda x: x.items,
            limit=limit,
            request=request,
        )
        return TrajectoryList(items)

    def list_data(
        self,
        sequence_external_id: str,
        measured_depth: Optional[DistanceRange] = None,
        true_vertical_depth: Optional[DistanceRange] = None,
    ) -> TrajectoryRows:
        """Get trajectory data

        Args:
            sequence_external_id (str): External id of a sequence ingested as a trajectory
            measured_depth (Optional[DistanceRange]): MD range
            true_vertical_depth (Optional[DistanceRange]): TVD range

        Returns:
            TrajectoryRows: Trajectory and iterator over rows
        """
        request = TrajectoryDataRequest(
            sequence_external_id=sequence_external_id,
            measured_depth=measured_depth,
            true_vertical_depth=true_vertical_depth,
        )
        path = self._get_path("/trajectories/data")
        response: Response = self.client.post(url_path=path, json=request.json())
        trajectory_data = TrajectoryData.parse_raw(response.text)
        return TrajectoryRows(trajectory_data)

    def interpolate(
        self,
        measured_depths: List[float],
        measured_depth_unit: str = "meter",
        true_vertical_depth_unit: str = "meter",
        *,
        wellbore_matching_id: Optional[str] = None,
        wellbore_asset_external_id: Optional[str] = None,
        ignore_unknown_measured_depths: Optional[bool] = False,
    ) -> TrueVerticalDepthList:
        """Get the true vertical depth corresponding to a list of measured depths

        The interpolation uses the minimum curvature method between trajectory
        points.

        Args:
            measured_depths (List[float]): List of measured depths.
            measured_depth_unit (str, optional): Unit for the measured depths. Defaults to "meter".
            true_vertical_depth_unit (str, optional): Unit for the returned true vertical depths. Defaults to "meter".
            wellbore_matching_id (str, optional)
            wellbore_asset_external_id (str, optional)
            ignore_unknown_measured_depths (bool, optional): set to True to ignore measured depths that are outside the trajectory

        Returns:
            :class:`~cognite.well_model.models.resource_list.TrueVerticalDepthList`: A list of true vertical depths corresponding to the given measured depths.

        Examples:
            Interpolate measured depths
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> tvds = wm.trajectories.interpolate(
                ...     wellbore_asset_external_id="VOLVE:13/10-F-11 T2",
                ...     measured_depths=[100.0, 150.0, 200.0, 250.0]
                ... )
                >>> tvds.true_vertical_depths
                [100.0, 150.0, 200.0, 250.0]

            Detect unknown depth
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> unreasonably_deep = 1000000000000000.0
                >>> tvds = wm.trajectories.interpolate(
                ...     wellbore_asset_external_id="VOLVE:13/10-F-11 T2",
                ...     measured_depths=[100.0, 150.0, 200.0, 250.0, unreasonably_deep],
                ...     ignore_unknown_measured_depths=True,
                ... )
                >>> unreasonably_deep in tvds.measured_depths
                False
                >>> # tvds.find(unreasonably_deep) will Raise a ValueError
                >>> tvds.find(200.0)
                200.0
        """  # noqa: E501
        identifier = create_identifier(
            external_id=wellbore_asset_external_id,
            matching_id=wellbore_matching_id,
        )
        tvd_unit = DistanceUnit(unit=create_distance_unit(true_vertical_depth_unit))
        md_unit = DistanceUnit(unit=create_distance_unit(measured_depth_unit))

        request = TrajectoryInterpolationRequestItems(
            items=[
                TrajectoryInterpolationRequest(
                    wellbore_id=identifier,
                    measured_depths=measured_depths,
                    measured_depth_unit=md_unit,
                    true_vertical_depth_unit=tvd_unit,
                )
            ],
            ignore_unknown_measured_depths=ignore_unknown_measured_depths,
        )
        path = self._get_path("/trajectories/interpolate")
        response = self.client.post(path, request.json())
        interps = response.json()["items"]
        assert len(interps) == 1
        interp = TrueVerticalDepths.parse_obj(interps[0])
        assert interp.true_vertical_depth_unit == tvd_unit
        return TrueVerticalDepthList(interp.true_vertical_depths, interp.measured_depths)

    def ingest(self, ingestions: List[TrajectoryIngestion]) -> TrajectoryList:
        """Ingest trajectories

        Args:
            ingestions (List[TrajectoryIngestion]): List of trajectory ingestion objects

        Returns:
            TrajectoryList:
        """
        if len(ingestions) == 0:
            return TrajectoryList([])
        path = self._get_path("/trajectories")
        json = TrajectoryIngestionItems(items=ingestions).json()
        response: Response = self.client.post(path, json)

        return TrajectoryList([Trajectory.parse_obj(x) for x in response.json()["items"]])

    def delete(self, source_external_ids: List[str]) -> List[str]:
        """Delete trajectories

        Args:
            source_external_ids (List[str]): List of external ids for a source for trajectory

        Returns:
            List[str]: List of external ids for a source for deleted trajectory
        """
        body = DeleteSequenceSources(
            items=[SequenceExternalId(sequence_external_id=external_id) for external_id in source_external_ids]
        )
        path: str = self._get_path("/trajectories/delete")
        response: Response = self.client.post(url_path=path, json=body.json())
        response_parsed: DeleteSequenceSources = DeleteSequenceSources.parse_raw(response.text)
        return [s.sequence_external_id for s in response_parsed.items]
