from unittest import TestCase
from unittest.mock import patch

from airflow import AirflowException
from airflow.models import Connection
from pycarlo.core import Session

from airflow_mcd.hooks import SessionHook

SAMPLE_ID = 'foo'
SAMPLE_TOKEN = 'bar'
SAMPLE_CONN_ID = 'mcd_default_session'


class SessionHookTest(TestCase):
    def setUp(self) -> None:
        self._session = SessionHook(mcd_session_conn_id=SAMPLE_CONN_ID)

    def test_session_id_is_set(self):
        self.assertEqual(self._session.mcd_session_conn_id, SAMPLE_CONN_ID)

    @patch('airflow_mcd.hooks.session_hook.Session')
    @patch.object(SessionHook, 'get_connection')
    def test_get_conn_with_extra(self, get_connection_mock, session_mock):
        get_connection_mock.return_value = Connection(extra={
            'mcd_id': SAMPLE_ID,
            'mcd_token': SAMPLE_TOKEN
        })
        expected_session = Session(mcd_id=SAMPLE_ID, mcd_token=SAMPLE_TOKEN)
        session_mock.return_value = expected_session

        self.assertEqual(self._session.get_conn(), expected_session)
        get_connection_mock.assert_called_once_with(SAMPLE_CONN_ID)
        session_mock.assert_called_once_with(mcd_id=SAMPLE_ID, mcd_token=SAMPLE_TOKEN)

    @patch('airflow_mcd.hooks.session_hook.Session')
    @patch.object(SessionHook, 'get_connection')
    def test_get_conn_with_login_and_password(self, get_connection_mock, session_mock):
        get_connection_mock.return_value = Connection(login=SAMPLE_ID, password=SAMPLE_TOKEN)
        expected_session = Session(mcd_id=SAMPLE_ID, mcd_token=SAMPLE_TOKEN)
        session_mock.return_value = expected_session

        self.assertEqual(self._session.get_conn(), expected_session)
        get_connection_mock.assert_called_once_with(SAMPLE_CONN_ID)
        session_mock.assert_called_once_with(mcd_id=SAMPLE_ID, mcd_token=SAMPLE_TOKEN)

    @patch('airflow_mcd.hooks.session_hook.Session')
    @patch.object(SessionHook, 'get_connection')
    def test_get_conn_with_non_default_host(self, get_connection_mock, session_mock):
        host = 'http://localhost:8080'
        get_connection_mock.return_value = Connection(host=host, login=SAMPLE_ID, password=SAMPLE_TOKEN)
        expected_session = Session(mcd_id=SAMPLE_ID, mcd_token=SAMPLE_TOKEN)
        session_mock.return_value = expected_session

        self.assertEqual(self._session.get_conn(), expected_session)
        get_connection_mock.assert_called_once_with(SAMPLE_CONN_ID)
        session_mock.assert_called_once_with(
            endpoint=f'{host}/graphql',
            mcd_id=SAMPLE_ID,
            mcd_token=SAMPLE_TOKEN
        )

    @patch('airflow_mcd.hooks.session_hook.Session')
    @patch.object(SessionHook, 'get_connection')
    def test_get_conn_with_non_default_host_including_path(self, get_connection_mock, session_mock):
        host = 'http://localhost:8080/graphql'
        get_connection_mock.return_value = Connection(host=host, login=SAMPLE_ID, password=SAMPLE_TOKEN)
        expected_session = Session(mcd_id=SAMPLE_ID, mcd_token=SAMPLE_TOKEN)
        session_mock.return_value = expected_session

        self.assertEqual(self._session.get_conn(), expected_session)
        get_connection_mock.assert_called_once_with(SAMPLE_CONN_ID)
        session_mock.assert_called_once_with(
            endpoint=host,
            mcd_id=SAMPLE_ID,
            mcd_token=SAMPLE_TOKEN
        )

    @patch.object(SessionHook, 'get_connection')
    def test_get_conn_with_incomplete_config(self, get_connection_mock):
        get_connection_mock.return_value = Connection()

        with self.assertRaises(AirflowException) as context:
            self._session.get_conn()
        self.assertEqual(str(context.exception), 'Missing expected key \'mcd_id\' from connection extra.')
