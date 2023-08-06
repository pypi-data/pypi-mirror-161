import time
from typing import Any, Dict, List

import pandas as pd

from cognite.well_model.wsfe.log_state_manager import LogStateManager, SummaryLogger
from cognite.well_model.wsfe.models import ProcessState, ProcessStatus


class ProcessStateList:
    _RESOURCE = None
    STATUS_COMPLETE = [ProcessStatus.ready, ProcessStatus.processing]

    def __init__(self, client, resources: List[ProcessState]):
        self._client = client
        self.data: List[ProcessState] = resources

    def dump(self, camel_case: bool = False) -> List[Dict[str, Any]]:
        """Dump the instance into a json serializable Python data type.

        Args:
            camel_case (bool): Use camelCase for attribute names. Defaults to False.

        Returns:
            List[Dict[str, Any]]: A list of dicts representing the instance.
        """
        return [resource.dump(camel_case=camel_case) for resource in self.data]

    def to_pandas(self, camel_case=True) -> pd.DataFrame:
        """Generate a Pandas Dataframe

        Args:
            camel_case (bool, optional): snake_case if false and camelCase if
                true. Defaults to True.

        Returns:
            DataFrame:
        """
        return pd.DataFrame(self.dump(camel_case=camel_case))

    def wait(self):
        """Wait until the all jobs have completed.

        While waiting, it will poll the service and print updates.
        """
        total = len(self.data)
        log_state = LogStateManager(total)
        summary_logger = SummaryLogger()
        while True:
            time.sleep(2)
            self.refresh_status()
            log_state.add_log(self.data, self._progress())
            summary_logger.print_summary_if_its_time(self.data)
            if self.is_complete():
                summary_logger.print_summary(self.data)
                return

    def is_complete(self) -> bool:
        return self._done_count() == len(self.data)

    def _done_count(self) -> int:
        COMPLETE = [ProcessStatus.done, ProcessStatus.error]
        return sum(1 for x in self.data if x.status in COMPLETE)

    def _progress(self) -> float:
        return self._done_count() / len(self.data)

    def refresh_status(self):
        """Refresh the statuses."""
        self.data = self._client.status([x.process_id for x in self.data]).data

    def _repr_html_(self):
        return self.to_pandas(camel_case=True)._repr_html_()

    def __getitem__(self, item):
        return self.data[item]

    def __iter__(self):
        return self.data.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self.data]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self.data.__len__()
