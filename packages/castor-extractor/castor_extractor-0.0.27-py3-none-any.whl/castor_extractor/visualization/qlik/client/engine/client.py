import logging

from .constants import MEASURES_SESSION_PARAMS, JsonRpcMethod
from .error import JsonRpcError
from .json_rpc import JsonRpcClient
from .websocket import open_websocket

logger = logging.getLogger(__name__)


def _handle(response: dict) -> int:
    """Returns the object Handle from the response payload"""
    return response["result"]["qReturn"]["qHandle"]


def _list_measures(client: JsonRpcClient, app_id: str) -> list:
    """
    Executes JSON-RPC messaging sequence to retrieve the list of measures
    for a given app

    references:
        - https://community.qlik.com/t5/Integration-Extension-APIs/How-to-ask-for-a-list-of-dimensions-and-measures-in-Qlik-Engine/td-p/1412156
        - https://help.qlik.com/en-US/sense-developer/May2021/Subsystems/EngineAPI/Content/Sense_EngineAPI/GenericObject/overview-generic-object.htm
    """
    response = client.send_message(
        method=JsonRpcMethod.OPEN_DOC,
        params=[app_id],
    )
    app_handle = _handle(response)

    response = client.send_message(
        method=JsonRpcMethod.CREATE_SESSION_OBJECT,
        handle=app_handle,
        params=list(MEASURES_SESSION_PARAMS),
    )
    session_handle = _handle(response)

    response = client.send_message(
        method=JsonRpcMethod.GET_LAYOUT,
        handle=session_handle,
    )
    return response["result"]["qLayout"]["qMeasureList"]["qItems"]


class EngineApiClient:
    """
    Engine API client is responsible to send the sequence of messages to
    get measures using JsonRpcClient and websocket connection.
    """

    def __init__(self, server_url: str, api_key: str):
        self.server_url = server_url
        self.api_key = api_key

    def measures(self, app_id: str, skip_access_denied: bool = True) -> list:
        """
        Opens a websocket and pass it to a JsonRpcClient to return the list
        of measures scoped on an app_id.

        By default, access_denied errors are skipped (logged as warning)
        """

        with open_websocket(
            app_id=app_id, server_url=self.server_url, api_key=self.api_key
        ) as websocket:
            json_rpc_client = JsonRpcClient(websocket=websocket)

            try:
                return _list_measures(json_rpc_client, app_id)
            except JsonRpcError as error:
                if skip_access_denied and error.is_access_denied:
                    logger.warning(error)
                    return []

                raise error
