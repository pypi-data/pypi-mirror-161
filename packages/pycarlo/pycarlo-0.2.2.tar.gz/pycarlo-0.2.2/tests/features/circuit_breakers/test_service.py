import copy
import json
from unittest import TestCase
from unittest.mock import patch, Mock

from box import Box

from pycarlo.core import Client
from pycarlo.features.circuit_breakers import CircuitBreakerService
from pycarlo.features.circuit_breakers.exceptions import CircuitBreakerPollException
from pycarlo.features.exceptions import CircuitBreakerPipelineException

SAMPLE_BREACH_COUNT = 42
SAMPLE_RULE_ID = '1234'
SAMPLE_JOB_EXECUTION = '5678'
SAMPLE_TRIGGER = Box({'trigger_circuit_breaker_rule': {'job_execution_uuid': SAMPLE_JOB_EXECUTION}})
SAMPLE_ERROR = Box(
    {'payload': {'error': "Exception('this is a test')", 'traceback': ['Line 10']}},
    default_box_attr=None,
    default_box=True
)


def sample_breach():
    return Box({'payload': {'breach_count': SAMPLE_BREACH_COUNT}}, default_box_attr=None, default_box=True)


class MockState:
    get_circuit_breaker_rule_state = Box(
        {'status': 'PROCESSING_COMPLETE', 'log': json.dumps([sample_breach()])},
        default_box=True
    )


class CircuitBreakerServiceTest(TestCase):
    def setUp(self) -> None:
        self._client_mock = Mock(spec=Client)

        self._service = CircuitBreakerService(mc_client=self._client_mock)

    @patch.object(CircuitBreakerService, 'poll')
    def test_trigger_and_poll_in_breach(self, poll_mock):
        poll_mock.return_value = SAMPLE_BREACH_COUNT
        self.assertTrue(self._test_trigger_and_poll(poll_mock=poll_mock))

    @patch.object(CircuitBreakerService, 'poll')
    def test_trigger_and_poll_no_breach(self, poll_mock):
        poll_mock.return_value = 0
        self.assertFalse(self._test_trigger_and_poll(poll_mock=poll_mock))

    @patch.object(CircuitBreakerService, 'trigger')
    def _test_trigger_and_poll(self, trigger_mock, poll_mock) -> bool:
        trigger_mock.return_value = SAMPLE_JOB_EXECUTION

        in_breach = self._service.trigger_and_poll(rule_uuid=SAMPLE_RULE_ID)
        trigger_mock.assert_called_once_with(rule_uuid=SAMPLE_RULE_ID)
        poll_mock.assert_called_once_with(job_execution_uuid=SAMPLE_JOB_EXECUTION, timeout_in_minutes=5)

        return in_breach

    def test_trigger(self):
        self._client_mock.return_value = SAMPLE_TRIGGER

        self.assertEqual(self._service.trigger(rule_uuid=SAMPLE_RULE_ID), SAMPLE_JOB_EXECUTION)
        self._client_mock.assert_called_once()
        self.assertEqual(
            self._trim_whitespace(self._client_mock.call_args[0][0]),
            self._trim_whitespace(
                f'mutation {{triggerCircuitBreakerRule(ruleUuid: "{SAMPLE_RULE_ID}") {{jobExecutionUuid}}}}')
        )

    @patch.object(CircuitBreakerService, '_poll')
    def test_poll_in_breach(self, internal_poll_mock):
        internal_poll_mock.return_value = sample_breach()
        self.assertEqual(self._service.poll(job_execution_uuid=SAMPLE_JOB_EXECUTION), SAMPLE_BREACH_COUNT)
        internal_poll_mock.assert_called_once_with(job_execution_uuid=SAMPLE_JOB_EXECUTION, timeout_in_minutes=5)

    @patch.object(CircuitBreakerService, '_poll')
    def test_poll_not_in_breach(self, internal_poll_mock):
        log = copy.deepcopy(sample_breach())
        log.payload.breach_count = 0

        internal_poll_mock.return_value = log
        self.assertEqual(self._service.poll(job_execution_uuid=SAMPLE_JOB_EXECUTION), 0)
        internal_poll_mock.assert_called_once_with(job_execution_uuid=SAMPLE_JOB_EXECUTION, timeout_in_minutes=5)

    @patch.object(CircuitBreakerService, '_poll')
    def test_poll_with_pipeline_error(self, internal_poll_mock):
        internal_poll_mock.return_value = SAMPLE_ERROR
        with self.assertRaises(CircuitBreakerPipelineException) as context:
            self._service.poll(job_execution_uuid=SAMPLE_JOB_EXECUTION)
        self.assertEqual(str(context.exception), f'Execution pipeline errored out. Details:\n{SAMPLE_ERROR}')

    @patch.object(CircuitBreakerService, '_poll')
    def test_poll_with_timeout(self, internal_poll_mock):
        internal_poll_mock.return_value = None
        with self.assertRaises(CircuitBreakerPollException) as context:
            self._service.poll(job_execution_uuid=SAMPLE_JOB_EXECUTION)
        self.assertEqual(str(context.exception), 'Polling timed out or contains a malformed log.')

    def test_internal_poll(self):
        self._client_mock.return_value = MockState
        self.assertEqual(
            self._service._poll(job_execution_uuid=SAMPLE_JOB_EXECUTION, timeout_in_minutes=10),
            sample_breach()
        )

    @patch('pycarlo.features.circuit_breakers.service.time')
    def test_internal_poll_with_timeout(self, mock_time):
        mock_time.time.side_effect = [1643751961, 1643752021, 1644356761]
        self.assertIsNone(self._service._poll(job_execution_uuid=SAMPLE_JOB_EXECUTION, timeout_in_minutes=10))
        mock_time.sleep.assert_called_once_with(15)

    @staticmethod
    def _trim_whitespace(_str: str) -> str:
        return ''.join(str(_str).split())
