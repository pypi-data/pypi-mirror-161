import logging
from typing import Iterable, List, Optional, Tuple, Union

from ...utils import (
    OUTPUT_DIR,
    current_timestamp,
    deep_serialize,
    from_env,
    get_output_filename,
    validate_baseurl,
    write_json,
    write_summary,
)
from .assets import QlikAsset
from .client import QlikClient
from .constants import API_KEY, BASE_URL

logger = logging.getLogger(__name__)


def iterate_all_data(
    client: QlikClient,
) -> Iterable[Tuple[QlikAsset, Union[list, dict]]]:
    """Iterate over the extracted data from Qlik"""

    logger.info("Extracting SPACES from REST API")
    spaces = client.fetch(QlikAsset.SPACES)
    yield QlikAsset.SPACES, deep_serialize(spaces)

    logger.info("Extracting USERS from REST API")
    users = client.fetch(QlikAsset.USERS)
    yield QlikAsset.USERS, deep_serialize(users)

    logger.info("Extracting APPS from REST API")
    apps = client.fetch(QlikAsset.APPS)
    yield QlikAsset.APPS, deep_serialize(apps)

    logging.info("Extracting LINEAGE data from REST API")
    lineage = client.fetch(QlikAsset.LINEAGE, apps=apps)
    yield QlikAsset.LINEAGE, deep_serialize(lineage)

    logging.info("Extracting MEASURES data from JSON-RPC API")
    measures = client.fetch(QlikAsset.MEASURES, apps=apps)
    yield QlikAsset.MEASURES, deep_serialize(measures)


def extract_all(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    output_directory: Optional[str] = None,
    except_http_error_statuses: Optional[List[int]] = None,
) -> None:
    """
    Extract data from Qlik REST API
    Store the output files locally under the given output_directory
    """

    _output_directory = output_directory or from_env(OUTPUT_DIR)
    _base_url = validate_baseurl(base_url or from_env(BASE_URL))
    _api_key = api_key or from_env(API_KEY)

    client = QlikClient(
        server_url=_base_url,
        api_key=_api_key,
        except_http_error_statuses=except_http_error_statuses,
    )

    ts = current_timestamp()

    for key, data in iterate_all_data(client):
        filename = get_output_filename(key.name.lower(), _output_directory, ts)
        write_json(filename, data)

    write_summary(_output_directory, ts, base_url=_base_url)
