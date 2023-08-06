import json
import time
from typing import Optional, Callable, Union
from uuid import UUID

from box import Box

from pycarlo.common import get_logger
from pycarlo.common.utils import boxify
from pycarlo.core import Client, Mutation, Query
from pycarlo.features.circuit_breakers.exceptions import CircuitBreakerPollException, CircuitBreakerPipelineException

logger = get_logger(__name__)


class CircuitBreakerService:
    _TERM_STATES = {'PROCESSING_COMPLETE', 'HAS_ERROR'}

    def __init__(self,
                 mc_client: Optional[Client] = None,
                 print_func: Optional[Callable] = logger.info):
        """
        Convenience methods to help with using circuit breaker rules.

        :param mc_client: MCD client (e.g. for creating a custom session); created otherwise.
        :param print_func: Function to use for echoing. Uses python logging by default, which requires setting MCD_VERBOSE_ERRORS.
        """
        self._client = mc_client or Client()
        self._print_func = print_func

    def trigger_and_poll(self, rule_uuid: Union[str, UUID], timeout_in_minutes: Optional[int] = 5) -> Optional[bool]:
        """
        Convenience method to both trigger and poll (wait) on circuit breaker rule execution.

        :param rule_uuid: UUID of the rule (custom SQL monitor) to execute.
        :param timeout_in_minutes: Polling timeout in minutes. See poll() for details.
        :return: True if rule execution is in breach; False otherwise. See poll() for any exceptions raised.
        """
        return bool(
            self.poll(
                job_execution_uuid=self.trigger(rule_uuid=rule_uuid),
                timeout_in_minutes=timeout_in_minutes
            )
        )

    def trigger(self, rule_uuid: Union[str, UUID]) -> str:
        """
        Trigger a rule to start execution with circuit breaker checkpointing.

        :param rule_uuid: UUID of the rule (custom SQL monitor) to execute.
        :return: Job execution UUID, as a string, to be used to retrieve execution state / status.
        """
        mutation = Mutation()
        mutation.trigger_circuit_breaker_rule(rule_uuid=str(rule_uuid)).__fields__('job_execution_uuid')
        job_execution_uuid = self._client(mutation).trigger_circuit_breaker_rule.job_execution_uuid
        self._print_func(f'Triggered rule with ID \'{rule_uuid}\'. Received \'{job_execution_uuid}\' as execution ID.')
        return job_execution_uuid

    def poll(self, job_execution_uuid: Union[str, UUID], timeout_in_minutes: Optional[int] = 5) -> Optional[int]:
        """
        Poll status / state of an execution for a triggered rule. Polls until status is in a term state or timeout.

        :param job_execution_uuid: UUID for the job execution of a rule (custom SQL monitor).
        :param timeout_in_minutes: Polling timeout in minutes. Note that The Data Collector Lambda has a max timeout of
        15 minutes when executing a query. Queries that take longer to execute are not supported, so we recommend
        filtering down the query output to improve performance (e.g limit WHERE clause). If you expect a query to
        take the full 15 minutes we recommend padding the timeout to 20 minutes.
        :return: Breach count. A greater than 0 value indicates a breach.
        :raise CircuitBreakerPipelineException: An error in executing the rule (e.g. error in query).
        :raise CircuitBreakerPollException: A timeout during polling or a malformed response.
        """
        log = self._poll(job_execution_uuid=job_execution_uuid, timeout_in_minutes=timeout_in_minutes)
        self._print_func(f'Completed polling. Retrieved execution with log \'{log}\' for ID \'{job_execution_uuid}\'.')

        if log and len(log) > 0:
            if log.payload.error:
                raise CircuitBreakerPipelineException(f'Execution pipeline errored out. Details:\n{log}')
            if log.payload.breach_count is not None:
                return log.payload.breach_count
        raise CircuitBreakerPollException

    @boxify(use_snakes=True, default_box_attr=None, default_box=True)
    def _poll(self,
              job_execution_uuid: Union[str, UUID],
              timeout_in_minutes: int,
              sleep_interval_in_seconds: Optional[int] = 15) -> Optional[Box]:
        timeout_start = time.time()
        while time.time() < timeout_start + 60 * timeout_in_minutes:
            query = Query()
            query.get_circuit_breaker_rule_state(job_execution_uuid=str(job_execution_uuid)).__fields__('status', 'log')
            circuit_breaker_state = self._client(query).get_circuit_breaker_rule_state
            self._print_func(f'Retrieved execution with status \'{circuit_breaker_state.status}\' for '
                             f'ID \'{job_execution_uuid}\'.')

            if circuit_breaker_state.status in self._TERM_STATES:
                return json.loads(circuit_breaker_state.log)[-1]

            self._print_func(f'State is not term for ID \'{job_execution_uuid}\'. Polling again '
                             f'in \'{sleep_interval_in_seconds}\' seconds.')
            time.sleep(sleep_interval_in_seconds)
