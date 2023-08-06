from typing import List, Union

from humanloop.api.models.log import Log, LogResponse
from humanloop.sdk.init import _get_client


def log(*args, **kwargs) -> Union[LogResponse, List[LogResponse]]:
    """Log a datapoint to Humanloop with optional feedback.

    This function accepts a single log, a list of logs, or a single log passed in as kwargs:
        - log(Log(...))
        - log([Log(...), Log(...)])
        - log(
            project: str
            inputs: KeyValues
            output: str
            model: Optional[str]
            prompt_template: Optional[str]
            source: str
            parameters: Optional[KeyValues]
            metadata: Optional[KeyValues]
            feedback: Optional[Union[Feedback, List[Feedback]]]
            created_at: Optional[datetime.datetime]
        )
    """
    if len(args) > 0:
        if len(args) != 1:
            raise ValueError(
                "When passing arguments, only a single argument is accepted. "
                "This should either be a single `Log` object or a list of `Log`s."
            )
        if len(kwargs) != 0:
            raise ValueError(
                "Either pass arguments of type `Log` or a list of `Log`s or the keyword arguments required by `Log` to the log() call, not both. "
                "See docstring for details."
            )
        return _log(args[0])
    elif len(kwargs) > 0:
        return _log(Log(**kwargs))
    else:
        raise ValueError(
            "Provide a `Log`, or a list of `Log`s, or the required keyword arguments to create a `Log` object. "
            "See docstring for details."
        )


def _log(log_data: Union[Log, List[Log]]):
    client = _get_client()
    return client.log(log_data).__root__
