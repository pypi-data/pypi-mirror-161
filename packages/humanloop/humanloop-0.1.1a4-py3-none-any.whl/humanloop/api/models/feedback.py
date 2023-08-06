from typing import List, Optional, Union

from pydantic import BaseModel

from .utils import RootBaseModel


class FeedbackResponse(BaseModel):
    id: str
    label: str
    group: str
    log_id: str
    source: Optional[str]


class ListFeedbackResponse(RootBaseModel):
    __root__: Union[FeedbackResponse, List[FeedbackResponse]]
