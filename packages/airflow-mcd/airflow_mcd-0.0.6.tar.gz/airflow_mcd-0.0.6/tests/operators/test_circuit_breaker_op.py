from unittest import TestCase
from unittest.mock import patch

from airflow import AirflowException
from airflow.exceptions import AirflowSkipException

from airflow_mcd.operators import SimpleCircuitBreakerOperator

SAMPLE_CONN_ID = 'mcd_default_session'
SAMPLE_RULE_ID = 'foo'
SAMPLE_TIMEOUT_IN_MINUTES = 10
SAMPLE_FAIL_OPEN = False


class CbOpTest(TestCase):
    def setUp(self) -> None:
        self._op = SimpleCircuitBreakerOperator(
            mcd_session_conn_id=SAMPLE_CONN_ID,
            rule_uuid=SAMPLE_RULE_ID,
            timeout_in_minutes=SAMPLE_TIMEOUT_IN_MINUTES,
            fail_open=SAMPLE_FAIL_OPEN,
            task_id='test'
        )

    def test_initialization(self):
        self.assertEqual(self._op.rule_uuid, SAMPLE_RULE_ID)
        self.assertEqual(self._op.timeout_in_minutes, SAMPLE_TIMEOUT_IN_MINUTES)
        self.assertEqual(self._op.fail_open, SAMPLE_FAIL_OPEN)
        self.assertEqual(self._op.mcd_session_conn_id, SAMPLE_CONN_ID)

    @patch.object(SimpleCircuitBreakerOperator, 'get_session')
    @patch('airflow_mcd.operators.circuit_breaker_operators.CircuitBreakerService')
    def test_execute_no_breach(self, cd_mock, get_session_mock):
        cd_mock().trigger_and_poll.return_value = False

        self.assertIsNone(self._op.execute())
        cd_mock().trigger_and_poll.assert_called_once_with(
            rule_uuid=SAMPLE_RULE_ID,
            timeout_in_minutes=SAMPLE_TIMEOUT_IN_MINUTES
        )
        get_session_mock.assert_called_once_with()

    @patch.object(SimpleCircuitBreakerOperator, 'get_session')
    @patch('airflow_mcd.operators.circuit_breaker_operators.CircuitBreakerService')
    def test_execute_with_breach(self, cd_mock, get_session_mock):
        cd_mock().trigger_and_poll.return_value = True

        with self.assertRaises(AirflowException) as context:
            self._op.execute()
        self.assertEqual(str(context.exception), f'Rule \'{SAMPLE_RULE_ID}\' is in breach!')
        cd_mock().trigger_and_poll.assert_called_once_with(
            rule_uuid=SAMPLE_RULE_ID,
            timeout_in_minutes=SAMPLE_TIMEOUT_IN_MINUTES
        )
        get_session_mock.assert_called_once_with()

    @patch.object(SimpleCircuitBreakerOperator, 'get_session')
    @patch('airflow_mcd.operators.circuit_breaker_operators.CircuitBreakerService')
    def test_execute_with_breach_and_fail_closed(self, cd_mock, get_session_mock):
        cd_mock().trigger_and_poll.side_effect = ValueError

        with self.assertRaises(AirflowException):
            self._op.execute()
        cd_mock().trigger_and_poll.assert_called_once_with(
            rule_uuid=SAMPLE_RULE_ID,
            timeout_in_minutes=SAMPLE_TIMEOUT_IN_MINUTES
        )
        get_session_mock.assert_called_once_with()

    @patch.object(SimpleCircuitBreakerOperator, 'get_session')
    @patch('airflow_mcd.operators.circuit_breaker_operators.CircuitBreakerService')
    def test_execute_with_breach_and_fail_open(self, cd_mock, get_session_mock):
        op = SimpleCircuitBreakerOperator(
            mcd_session_conn_id=SAMPLE_CONN_ID,
            rule_uuid=SAMPLE_RULE_ID,
            timeout_in_minutes=SAMPLE_TIMEOUT_IN_MINUTES,
            fail_open=True,
            task_id='test'
        )
        cd_mock().trigger_and_poll.side_effect = ValueError

        with self.assertRaises(AirflowSkipException) as context:
            op.execute()
        cd_mock().trigger_and_poll.assert_called_once_with(
            rule_uuid=SAMPLE_RULE_ID,
            timeout_in_minutes=SAMPLE_TIMEOUT_IN_MINUTES
        )
        get_session_mock.assert_called_once_with()
        self.assertEqual((str(context.exception)), 'Encountered an error when executing the rule, but failing open.')
