from typing import Any, Dict, List

from cognite.well_model.client.models.resource_list import WDLResourceList
from cognite.well_model.client.utils._auxiliary import to_camel_case
from cognite.well_model.models import Duration, DurationUnitEnum, NptAggregateRow


class NptAggregateRowList(WDLResourceList):
    _RESOURCE = NptAggregateRow

    def __init__(self, resources: List[NptAggregateRow], wellbore_matching_id: str):
        super().__init__(resources)
        self.wellbore_matching_id = wellbore_matching_id
        self.duration = Duration(
            value=sum(x.duration.value if x.duration else 0 for x in resources), unit=DurationUnitEnum.hour
        )
        self.count = sum(x.count for x in resources)

    def dump(self, camel_case: bool = False) -> List[Dict[str, Any]]:
        change_key = to_camel_case if camel_case else lambda x: x
        return [
            {
                change_key("wellbore_matching_id"): self.wellbore_matching_id,
                **resource.dump(camel_case=camel_case),
            }
            for resource in self.data
        ]


class NptAggregateList(WDLResourceList):
    _RESOURCE = NptAggregateRowList

    def __init__(self, resources: List[NptAggregateRowList]):
        super().__init__(resources)

    def dump(self, camel_case: bool = False) -> List[Dict[str, Any]]:
        change_key = to_camel_case if camel_case else lambda x: x
        output = []
        data: List[NptAggregateRowList] = self.data
        for item in data:
            row = {
                change_key("wellbore_matching_id"): item.wellbore_matching_id,
                "duration": item.duration.value if item.duration else None,
                change_key("duration_unit"): item.duration.unit.name if item.duration else None,
                "count": item.count,
            }
            output.append(row)
        return output
