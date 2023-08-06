import requests
from uplink import Body, Consumer, get, json, post, response_handler, returns
from uplink.auth import ApiTokenHeader

from humanloop.api.models.feedback import ListFeedbackResponse
from humanloop.api.models.log import (
    ListFeedbackRequest,
    ListLogRequest,
    ListLogResponse,
)
from humanloop.api.models.user import UserResponse


def raise_for_status(response: requests.Response):
    """Checks whether or not the response was successful."""
    response.raise_for_status()
    return response


@response_handler(raise_for_status)
class Humanloop(Consumer):
    """Python Client for the Humanloop API"""

    @returns.json()
    @get()
    def health_check(self):
        """Health check"""
        pass

    @returns.json()
    @get("/users/me")
    def read_me(self) -> UserResponse:
        """Validate user exists with valid password and return access token"""
        pass

    @json
    @returns.json
    @post("/logs")
    def log(
        self,
        request: Body(type=ListLogRequest),
    ) -> ListLogResponse:
        """Log a datapoint to your Humanloop project."""

    @json
    @returns.json
    @post("/feedback")
    def feedback(
        self, feedback: Body(type=ListFeedbackRequest)
    ) -> ListFeedbackResponse:
        """Add feedback to an existing logged datapoint."""


def get_humanloop_client(api_key: str, base_url: str) -> Humanloop:
    return Humanloop(base_url=base_url, auth=ApiTokenHeader("X-API-KEY", api_key))
