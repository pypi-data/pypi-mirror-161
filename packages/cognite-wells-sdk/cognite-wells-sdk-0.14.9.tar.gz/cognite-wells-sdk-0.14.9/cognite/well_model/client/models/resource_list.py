import json
from typing import Any, Dict, List

from pandas import DataFrame

from cognite.well_model.client.utils._auxiliary import to_camel_case
from cognite.well_model.models import (
    CasingSchematic,
    DepthMeasurement,
    HoleSection,
    HoleSectionGroup,
    IncompleteWell,
    MeasurementTypeDetails,
    MnemonicMatchGroup,
    Nds,
    Npt,
    Source,
    SummaryCount,
    TimeMeasurement,
    Trajectory,
    Well,
    Wellbore,
    WellPropertiesSummaryRow,
    WellTops,
    WellWellheadView,
)


def _dump_fix_case_and_nulls(items, camel_case) -> List[Dict[str, Any]]:
    change_key = to_camel_case if camel_case else lambda x: x
    output = []
    for item in items:
        output_item = {change_key(k): v for k, v in item.items() if v is not None}
        output.append(output_item)
    return output


class WDLResourceList:
    _RESOURCE = None

    def __init__(self, resources: List[Any]):
        self.data = resources
        for resource in resources:
            if resource is None or not isinstance(resource, self._RESOURCE):  # type: ignore
                raise TypeError(
                    f"All resources for class '{self.__class__.__name__}' must be of type"  # type: ignore
                    f" '{self._RESOURCE.__name__}', "
                    f"not '{type(resource)}'. "
                )

    def dump(self, camel_case: bool = False) -> List[Dict[str, Any]]:
        """Dump the instance into a json serializable Python data type.

        Args:
            camel_case (bool): Use camelCase for attribute names. Defaults to False.

        Returns:
            List[Dict[str, Any]]: A list of dicts representing the instance.
        """
        return [resource.dump(camel_case=camel_case) for resource in self.data]

    def to_pandas(self, camel_case=True) -> DataFrame:
        """Generate a Pandas Dataframe

        Args:
            camel_case (bool, optional): snake_case if false and camelCase if
                true. Defaults to True.

        Returns:
            DataFrame:
        """
        rows = []
        for dump_row in self.dump(camel_case=camel_case):
            row = {}
            for key, value in dump_row.items():
                if isinstance(value, list) or isinstance(value, dict):
                    row[key] = json.dumps(value)
                else:
                    row[key] = value
            rows.append(row)
        return DataFrame(rows)

    def _repr_html_(self):
        return self.to_pandas()._repr_html_()

    def __getitem__(self, item):
        return self.data[item]

    def __iter__(self):
        return self.data.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self.data]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self.data.__len__()


class WellList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Well` objects"""

    _RESOURCE = Well

    def wellbores(self):
        """Get a merged list of all wellbores from all wells in the list

        Returns:
            :class:`~cognite.well_model.models.Wellbore`: A merged list of all wellbores from all wells in the list .
        """
        wellbores: List[Wellbore] = []
        for w in self.data:
            for wb in w.wellbores:
                wellbores.append(wb)
        return WellboreList(wellbores)


class IncompleteWellList(WDLResourceList):
    _RESOURCE = IncompleteWell


class WellboreList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Wellbore` objects"""

    _RESOURCE = Wellbore


class NptList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Npt` objects"""

    _RESOURCE = Npt


class TrajectoryList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Trajectory` objects"""

    _RESOURCE = Trajectory


class NdsList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Nds` objects"""

    _RESOURCE = Nds


class DepthMeasurementList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.DepthMeasurement` objects"""

    _RESOURCE = DepthMeasurement


class TimeMeasurementList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.TimeMeasurement` objects"""

    _RESOURCE = TimeMeasurement


class CasingsList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.CasingSchematic` objects"""

    _RESOURCE = CasingSchematic


class SourceList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.Source` objects"""

    _RESOURCE = Source


class WellTopsList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.WellTops` objects"""

    _RESOURCE = WellTops

    def dump(self, camel_case=False):
        return _dump_fix_case_and_nulls(
            camel_case=camel_case,
            items=[
                {
                    "wellbore_matching_id": welltop.wellbore_matching_id,
                    "wellbore_name": welltop.wellbore_name,
                    "sequence_external_id": welltop.source.sequence_external_id,
                    "source_name": welltop.source.source_name,
                    "tops_count": len(welltop.tops),
                }
                for welltop in self.data
            ],
        )


class WellPropertiesList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.WellPropertiesSummaryRow` objects"""

    _RESOURCE = WellPropertiesSummaryRow

    def dump(self, camel_case=False) -> List[Dict[str, Any]]:
        # Custom pandas implementation to make the column order deterministic
        # and to only show the columns that isn't all None's.
        return _dump_fix_case_and_nulls(
            camel_case=camel_case,
            items=[
                {
                    "region": row.region,
                    "country": row.country,
                    "block": row.block,
                    "field": row.field,
                    "quadrant": row.quadrant,
                    "operator": row.operator,
                    "wells_count": row.wells_count,
                }
                for row in self.data
            ],
        )


class MnemonicMatchList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.MnemonicMatchGroup` objects"""

    _RESOURCE = MnemonicMatchGroup

    def dump(self, camel_case=False) -> DataFrame:
        data: List[MnemonicMatchGroup] = self.data
        matches = []
        for group in data:
            for match in group.matches:
                matches.append(
                    {
                        "mnemonic": group.mnemonic,
                        "company_name": match.company_name,
                        "measurement_type": match.measurement_type,
                        "primary_quantity_class": match.primary_quantity_class,
                        "tools": json.dumps([tool.dict(by_alias=camel_case) for tool in match.tools]),
                    }
                )
        return _dump_fix_case_and_nulls(items=matches, camel_case=camel_case)


class SummaryList(WDLResourceList):
    """List of :class:`~cognite.well_model.models.SummaryCount` objects"""

    _RESOURCE = SummaryCount


class WellWellheadViewList(WDLResourceList):
    """List of :class:`cognite.well_model.models.WellWellheadView` objects"""

    _RESOURCE = WellWellheadView


class MeasurementTypeDetailsList(WDLResourceList):
    """List of :class:`cognite.well_model.models.MeasurementTypeDetails` objects"""

    _RESOURCE = MeasurementTypeDetails


class HoleSectionsList(WDLResourceList):
    """List of :class:`cognite.well_model.models.HoleSection` objects"""

    _RESOURCE = HoleSection


class HoleSectionGroupsList(WDLResourceList):
    """List of :class:`cognite.well_model.models.HoleSection` objects"""

    _RESOURCE = HoleSectionGroup
