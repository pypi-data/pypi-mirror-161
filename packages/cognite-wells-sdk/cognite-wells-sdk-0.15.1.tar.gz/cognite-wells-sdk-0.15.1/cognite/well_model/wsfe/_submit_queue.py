import logging
from time import sleep
from typing import List, Set

from cognite.well_model.wsfe.client import WellLogExtractorClient
from cognite.well_model.wsfe.log_state_manager import LogStateManager, SummaryLogger
from cognite.well_model.wsfe.models import ProcessState, ProcessStatus, SubmitJob
from cognite.well_model.wsfe.process_state_list import ProcessStateList

log = logging.getLogger(__name__)


class ClientSideSubmitQueue:
    """Client side queue for WSFE jobs.

    Makes sure that the WSFE is saturated with work while the server-side queue
    is reasonably small. This approach makes sure that the jobs are sent with
    refreshed tokens.
    """

    def __init__(
        self,
        client: WellLogExtractorClient,
        jobs: List[SubmitJob],
        max_active_jobs: int = 16,
        overwrite: bool = False,
        enable_time_series: bool = False,
    ):
        self._client = client
        self._jobs = list(jobs)
        self._jobs.reverse()
        self._states: List[ProcessState] = []
        self._total = len(jobs)
        self._max_active_jobs = max_active_jobs
        self._process_ids: Set[str] = set()
        self._overwrite = overwrite
        self._enable_time_series = enable_time_series

        self._manager = LogStateManager(self._total)
        self._summary_printer = SummaryLogger()

    def done_count(self) -> int:
        COMPLETE = [ProcessStatus.done, ProcessStatus.error]
        return sum(1 for x in self._states if x.status in COMPLETE)

    def working_count(self) -> int:
        WORKING = [ProcessStatus.ready, ProcessStatus.processing]
        return sum(1 for x in self._states if x.status in WORKING)

    def is_complete(self) -> bool:
        return self.done_count() == self._total

    def progress(self) -> float:
        return self.done_count() / self._total

    def run(self) -> ProcessStateList:
        self.send_new_jobs()
        while not self.is_complete():
            self.update_state()
            self._manager.add_log(self._states, self.progress())
            self._summary_printer.print_summary_if_its_time(self._states)
            if self.is_complete():
                break
            self.send_new_jobs()
            sleep(2.0)
        self._summary_printer.print_summary(self._states)
        return ProcessStateList(self._client, self._states)

    def send_new_jobs(self):
        num_new_jobs = self._max_active_jobs - self.working_count()
        new_jobs = []
        while self._jobs and len(new_jobs) < num_new_jobs:
            new_jobs.append(self._jobs.pop())
        if new_jobs:
            log.info(f"Sending {len(new_jobs)} new jobs to wsfe")
            result = self._client.submit(
                new_jobs,
                overwrite=self._overwrite,
                enable_time_series=self._enable_time_series,
            )
            for state in result.data:
                self._process_ids.add(state.process_id)

    def update_state(self):
        self._states = self._client.status(list(self._process_ids)).data
