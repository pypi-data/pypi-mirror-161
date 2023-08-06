from typing import Dict
from urllib.parse import urlparse, urlunparse

from airflow import AirflowException
from airflow.models.connection import Connection

try:
    from airflow.hooks.base import BaseHook

    HOOK_SOURCE = None
except ImportError:
    # For Airflow 1.10.*
    from airflow.hooks.base_hook import BaseHook

    HOOK_SOURCE = 'mcd_session'
from pycarlo.core import Session


class SessionHook(BaseHook):
    API_PATH = '/graphql'

    def __init__(self, mcd_session_conn_id: str):
        """
        MCD Session Hook. Retrieves connection details from the Airflow `Connection` object.

        The `mcd_id` can be configured via the connection "login", and the `mcd_token` via the connection "password".

        Alternatively, either `mcd_id` or `mcd_token` can be configured in the connection "extra", with values passed
        via "login" or "password" taking precedence.
        {
            "mcd_id": "foo",
            "mcd_token": "bar"
        }

        :param mcd_session_conn_id: Connection ID for the MCD session.
        """
        self.mcd_session_conn_id = mcd_session_conn_id

        super().__init__(**(dict(source=HOOK_SOURCE) if HOOK_SOURCE is not None else {}))

    def get_conn(self) -> Session:
        """
        Gets a connection for the hook.

        :return: MCD access session.
        """
        connection = self.get_connection(self.mcd_session_conn_id)
        connection_extra = connection.extra_dejson
        try:
            return Session(
                mcd_id=connection.login or connection_extra['mcd_id'],
                mcd_token=connection.password or connection_extra['mcd_token'],
                **self._get_session_extra(connection)
            )
        except KeyError as err:
            raise AirflowException(f'Missing expected key {err} from connection extra.')

    def _get_session_extra(self, connection: Connection) -> Dict:
        """
        Extract extra MCD session parameters from an Airflow connection.

        :param connection: Airflow connection
        :return: dictionary of kwargs for MCD Session
        """
        extras = {}
        if connection.host:
            extras['endpoint'] = self._get_api_endpoint(connection.host)
        return extras

    def _get_api_endpoint(self, host: str) -> str:
        """
        Get MCD API endpoint from Airflow connection host.

        :param host: Airflow connection host
        :return: MCD API endpoint url
        """
        parsed = urlparse(host)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path or self.API_PATH,  # set root API path if not provided in connection host
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
