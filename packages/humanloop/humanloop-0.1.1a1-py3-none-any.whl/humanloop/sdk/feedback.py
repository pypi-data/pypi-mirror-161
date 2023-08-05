from typing import List, Union

from humanloop.api.models.feedback import FeedbackResponse
from humanloop.api.models.log import Feedback
from humanloop.sdk.init import _get_client


def feedback(
    feedback: Union[Feedback, List[Feedback]]
) -> Union[FeedbackResponse, List[FeedbackResponse]]:
    """Provide feedback on a logged completion."""
    client = _get_client()
    return client.feedback(feedback=feedback).__root__
