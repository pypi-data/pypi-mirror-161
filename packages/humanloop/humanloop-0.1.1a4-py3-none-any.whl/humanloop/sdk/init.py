from typing import Optional

from humanloop.api.client import Humanloop, get_humanloop_client
from humanloop.shared.console import console
from humanloop.shared.settings import get_humanloop_settings

client: Optional[Humanloop] = None


def _get_client() -> Humanloop:
    """Gets the initialized API client or attempts to initialize one from the environment."""
    global client
    if client is None:
        init()
    return client


def _clear_client() -> None:
    global client
    client = None


def init(api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
    """Initialize a Humanloop API client to use the SDK

    Args:
        api_key: Your Humanloop API key
        base_url: The base URL for the Humanloop API to connect to

    Returns:
        None
    """
    # Use settings variables if provided here.
    settings_overrides = {}
    if api_key is not None:
        settings_overrides["api_key"] = api_key
    if base_url is not None:
        settings_overrides["api_base_url"] = base_url

    settings = get_humanloop_settings(**settings_overrides)
    api_key = settings.api_key
    base_url = settings.api_base_url

    if api_key is None:
        console.print(
            "[error]Attempting to initialize API client with no API key.[/error]"
        )
        console.print(
            "Either pass a valid API key to `hl.init()` or set the `HUMANLOOP_API_KEY` environment variable."
        )
        raise ValueError("No API key provided")
    if base_url is None:
        console.print(
            "[error]Attempting to initialize API client with no API base URL.[/error]"
        )
        console.print(
            "Either pass a valid API base URL to `hl.init()` or set the `HUMANLOOP_API_BASE_URL` environment variable."
        )
        raise ValueError("No API base URL provided")

    console.print(f"Connecting to API at {base_url} with key {'*' * len(api_key)}")

    global client
    client = get_humanloop_client(
        api_key=api_key,
        base_url=base_url,
    )
