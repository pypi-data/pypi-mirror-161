from typing import List, Union

from humanloop.api.models.feedback import FeedbackResponse
from humanloop.api.models.log import Feedback
from humanloop.sdk.init import _get_client


def feedback(*args, **kwargs) -> Union[FeedbackResponse, List[FeedbackResponse]]:
    """Provide feedback on a logged completion.

    This function accepts a single `Feedback`, a list of `Feedback`s, or a single feedback passed in as kwargs:
        - feedback(Feedback(...))
        - feedback([Feedback(...), Feedback(...)])
        - feedback(
            group: str
            label: str
            log_id: str
            source: Optional[str]
        )
    """
    if len(args) > 0:
        if len(args) != 1:
            raise ValueError(
                "When passing arguments, only a single argument is accepted. "
                "This should either be a single `Feedback` object or a list of `Feedback`s."
            )
        if len(kwargs) != 0:
            raise ValueError(
                "Either pass arguments of type `Feedback` or a list of `Feedback`s or the keyword arguments required by `Feedback` to the feedback() call, not both. "
                "See docstring for details."
            )
        return _feedback(args[0])
    elif len(kwargs) > 0:
        return _feedback(Feedback(**kwargs))
    else:
        raise ValueError(
            "Provide a `Feedback`, or a list of `Feedback`s, or the required keyword arguments to create a `Feedback` object. "
            "See docstring for details."
        )


def _feedback(feedback: Union[Feedback, List[Feedback]]):
    client = _get_client()
    return client.feedback(feedback=feedback).__root__
