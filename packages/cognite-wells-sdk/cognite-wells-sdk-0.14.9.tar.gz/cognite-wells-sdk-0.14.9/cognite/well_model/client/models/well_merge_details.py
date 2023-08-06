from typing import Any, Dict, List

import pandas as pd

from cognite.well_model.client.models.wellbore_merge_details import _to_pandas_value
from cognite.well_model.client.utils._auxiliary import to_camel_case
from cognite.well_model.models import FieldSources, Well, WellMergeDetails


class WellMergeDetailResource:
    def __init__(self, item: WellMergeDetails):
        self._data = item

    @property
    def well(self) -> Well:
        """Retrieve the well data

        Returns:
            Well: well
        """
        return self._data.well

    @property
    def field_sources(self) -> FieldSources:
        """Get the field sources.

        Returns:
            FieldSources: Field sources
        """
        fs: FieldSources = self._data.field_sources
        return fs

    def dump(self, camel_case=False) -> List[Dict[str, Any]]:
        change_key = to_camel_case if camel_case else lambda x: x
        well_dict = self.well.__dict__
        field_sources = self.field_sources.dict(by_alias=False)

        data = []
        for field, source in field_sources.items():
            field_data = {
                "property": change_key(field),
                "value": _to_pandas_value(well_dict[field]),
            }
            if source:
                field_data[change_key("source_name")] = source["source_name"]
                field_data[change_key("asset_external_id")] = source["asset_external_id"]
            data.append(field_data)
        return data

    def to_pandas(self, camel_case=True) -> pd.DataFrame:
        """Create a pandas data frame

        Returns:
            pd.DataFrame: Data frame
        """
        return pd.DataFrame(self.dump(camel_case=camel_case)).set_index("property")

    def _repr_html_(self):
        return self.to_pandas()._repr_html_()

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        return self._data.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self._data]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self._data.__len__()


class WellMergeDetailList:
    def __init__(self, items: List[WellMergeDetailResource]):
        self._items = items

    def dump(self, camel_case=False) -> List[Dict[str, Any]]:
        change_key = to_camel_case if camel_case else lambda x: x
        dumps = []
        for item in self._items:
            dump = [
                {
                    **x,
                    change_key("well_matching_id"): item.well.matching_id,
                    change_key("well_name"): item.well.name,
                }
                for x in item.dump(camel_case=camel_case)
            ]

            dumps += dump
        return dumps

    def to_pandas(self, camel_case=True) -> pd.DataFrame:
        """Create pandas data frame that combines data from multiple wells.

        Returns:
            pd.DataFrame: Data frame
        """
        change_key = to_camel_case if camel_case else lambda x: x
        if not self._items:
            return pd.DataFrame()
        return pd.DataFrame(self.dump(camel_case=camel_case)).set_index(change_key("well_matching_id"))

    def _repr_html_(self):
        return self.to_pandas()._repr_html_()

    def __getitem__(self, item):
        return self._items[item]

    def __iter__(self):
        return self._items.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self._items]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self._items.__len__()
