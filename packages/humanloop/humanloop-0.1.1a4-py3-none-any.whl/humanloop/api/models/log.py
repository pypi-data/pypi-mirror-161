import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .utils import RootBaseModel

KeyValues = Dict[str, Union[str, int, float]]


class Feedback(BaseModel):
    group: str
    label: str
    log_id: Optional[str] = Field(
        title="Optional log id for your feedback",
        description="log_id must be provided when adding feedback to an existing log. "
        "When feedback is included in hl.log, log_id is not required.",
    )
    source: Optional[str]


class ListFeedbackRequest(RootBaseModel):
    __root__: Union[Feedback, List[Feedback]]


class Log(BaseModel):
    project: str = Field(
        title="Project name",
        description="Unique project name. If it does not exist, a new project will "
        "be created.",
    )
    inputs: KeyValues = Field(
        title="Model input data",
        description="List of name, value pairs for the inputs used by your prompt "
        "template, or directly by your model.",
    )
    output: str = Field(
        title="Model output",
        description="Generated output from your model for the provided inputs, or your "
        "corrected generation.",
    )
    model: Optional[str] = Field(
        title="Type of model used",
        description="What model type was used for the generation? e.g. text-davinci-002. "
        "This can be null if the generation is user provided",
    )
    prompt_template: Optional[str] = Field(
        title="Prompt template",
        description="Prompt template that incorporated your specified inputs to form "
        "your final request to the model.",
    )
    source: str = Field(
        title="Source of generation",
        description="What was used to generate the output? e.g. gpt-3. "
        "In the case of logging corrections, or Human generated examples, the source "
        "can be set as a unique user reference.",
    )
    parameters: Optional[KeyValues] = Field(
        title="Model parameters",
        description="The hyper-parameter settings that along with your model source "
        "and prompt template (if provided) will uniquely determine a model"
        " configuration on Humanloop. For example the temperature setting.",
    )
    metadata: Optional[KeyValues] = Field(
        title="Metadata",
        description="Any additional metadata that you would like to log for reference.",
    )
    feedback: Optional[Union[Feedback, List[Feedback]]] = Field(
        title="Feedback labels",
        description="Optional parameter to provide feedback with your logged datapoint.",
    )
    created_at: Optional[datetime.datetime] = Field(
        title="Created at",
        description="Timestamp for when the log was created. "
        "If not provided, the time the log call was made will be used "
        "as a timestamp.",
    )


class ListLogRequest(RootBaseModel):
    __root__: Union[Log, List[Log]]


class ModelConfigStatsResponse(BaseModel):
    feedback_group_id: int
    feedback_group_name: str
    feedback_label: str
    feedback_count: int


class ModelConfigResponse(BaseModel):
    id: str
    model_name: str
    prompt_template: Optional[str]
    parameters: Optional[dict]
    feedback_stats: Optional[List[ModelConfigStatsResponse]]
    num_datapoints: Optional[int]
    last_used: Optional[datetime.datetime]
    created_at: datetime.datetime
    updated_at: datetime.datetime


class LogResponse(BaseModel):
    id: str


class ListLogResponse(RootBaseModel):
    __root__: Union[LogResponse, List[LogResponse]]
