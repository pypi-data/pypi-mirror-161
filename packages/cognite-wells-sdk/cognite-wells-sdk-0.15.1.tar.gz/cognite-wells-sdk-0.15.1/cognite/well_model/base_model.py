import enum
import json
from typing import Any, Dict, Iterable

from pandas import DataFrame
from pydantic import BaseModel
from pydantic.main import Extra

from cognite.well_model.client.utils._auxiliary import to_camel_case

DEFAULT_IGNORE = ("rows", "wellbores")


class WellsBaseModel(BaseModel):
    """
    The datamodel-code-generator program solves snake_case a bit opposite of
    what we want. We want to use `asset_id` in code, and `assetId` in json.
    Since it uses snake_case in the model and camelCase in the alias, we have to
    generate dict() and json() by alias, so that the output is true to the
    openapi spec.
    """

    class Config:
        extra = Extra.ignore

    def dict(self, by_alias=True, **kwargs):
        return super().dict(by_alias=by_alias, **kwargs)

    def json(self, by_alias=True, **kwargs):
        return super().json(by_alias=by_alias, **kwargs)

    def dump(self, ignore: Iterable[str] = DEFAULT_IGNORE, camel_case: bool = False) -> Dict[str, Any]:
        """Dump the instance into a json serializable Python data type.

        Args:
            ignore (List[str]): attributes that should not be added to the dataframe
            camel_case (bool): Use camelCase for attribute names. Defaults to False.

        Returns:
            List[Dict[str, Any]]: A list of dicts representing the instance.
        """

        from cognite.well_model.models import (  # To avoid circular import
            AssetSource,
            Datum,
            Distance,
            DistanceRange,
            DoglegSeverity,
            Duration,
            DurationRange,
            EventSource,
            GeneralExternalId,
            SequenceSource,
            Wellhead,
        )

        output: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if value is None or key.startswith("_"):
                continue
            if key in ignore:
                continue
            if type(value) == list:
                if len(value) == 0:
                    output[key] = "[]"
                else:
                    if isinstance(value[0], WellsBaseModel):
                        output[key] = [x.dict(by_alias=camel_case) for x in value]
                    else:
                        output[key] = [str(x) for x in value]
            elif isinstance(value, enum.Enum):
                output[key] = value.name
            elif isinstance(value, DurationRange):
                output[f"{key}_min"] = value.min
                output[f"{key}_max"] = value.max
                output[f"{key}_unit"] = value.unit.name
            elif isinstance(value, Duration):
                output[key] = value.value
                output[f"{key}_unit"] = value.unit.name
            elif isinstance(value, DistanceRange):
                output[f"{key}_min"] = value.min
                output[f"{key}_max"] = value.max
                output[f"{key}_unit"] = value.unit.name
            elif isinstance(value, Wellhead):
                output[f"{key}_x"] = value.x
                output[f"{key}_y"] = value.y
                output[f"{key}_crs"] = value.crs
            elif isinstance(value, Datum):
                output[key] = value.value
                output[key + "_unit"] = value.unit.name
                output[key + "_reference"] = value.reference
            elif isinstance(value, Distance):
                output[key] = value.value
                output[key + "_unit"] = value.unit.name
            elif isinstance(value, AssetSource):
                output["source_name"] = value.source_name
                output["source_asset_external_id"] = value.asset_external_id
            elif isinstance(value, DoglegSeverity):
                output[key] = value.value
                distance_unit = f"{value.unit.distance_interval:.0f} {value.unit.distance_unit}"
                output[key + "_unit"] = f"{value.unit.angle_unit}/{distance_unit}"
            elif isinstance(value, EventSource):
                output["source_name"] = value.source_name
                output["source_event_external_id"] = value.event_external_id
            elif isinstance(value, SequenceSource):
                output["source_name"] = value.source_name
                output["source_sequence_external_id"] = value.sequence_external_id
            elif isinstance(value, GeneralExternalId):
                output[f"{key}_external_id"] = value.external_id
                output[f"{key}_type"] = value.type.name
            elif isinstance(value, WellsBaseModel):
                output[key] = value.json()
            else:
                output[key] = value

        change_key = to_camel_case if camel_case else lambda x: x
        return {change_key(k): v for k, v in output.items()}

    def to_pandas(
        self,
        ignore: Iterable[str] = DEFAULT_IGNORE,
        camel_case: bool = True,
    ) -> DataFrame:
        ignore = [] if ignore is None else ignore
        dumped = self.dump(ignore, camel_case=camel_case)
        df = DataFrame(columns=["value"])
        for name, value in dumped.items():
            if isinstance(value, list):
                value = json.dumps(value)
            df.loc[name] = [value]
        return df

    # override this method so that the default for jupyter is dataframe
    def _repr_html_(self):
        return self.to_pandas()._repr_html_()
