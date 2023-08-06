from typing import Any, Dict, List

from cognite.well_model.client.models.resource_list import WDLResourceList
from cognite.well_model.client.utils._auxiliary import to_camel_case
from cognite.well_model.models import NdsAggregateRow


class NdsAggregateRowList(WDLResourceList):
    _RESOURCE = NdsAggregateRow

    def __init__(self, resources: List[NdsAggregateRow], wellbore_matching_id: str):
        super().__init__(resources)
        self.wellbore_matching_id = wellbore_matching_id
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


class NdsAggregateList(WDLResourceList):
    _RESOURCE = NdsAggregateRowList

    def __init__(self, resources: List[NdsAggregateRowList]):
        super().__init__(resources)

    def dump(self, camel_case: bool = False) -> List[Dict[str, Any]]:
        change_key = to_camel_case if camel_case else lambda x: x
        output = []
        data: List[NdsAggregateRowList] = self.data
        for item in data:
            row = {
                change_key("wellbore_matching_id"): item.wellbore_matching_id,
                "count": item.count,
            }
            output.append(row)
        return output
