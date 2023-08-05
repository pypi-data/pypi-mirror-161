from typing import List, Union

from humanloop.api.models.log import Log, LogResponse
from humanloop.sdk.init import _get_client


def log(log_data: Union[Log, List[Log]]) -> Union[LogResponse, List[LogResponse]]:
    """Log a datapoint to Humanloop with optional feedback"""

    client = _get_client()
    return client.log(log_data).__root__
