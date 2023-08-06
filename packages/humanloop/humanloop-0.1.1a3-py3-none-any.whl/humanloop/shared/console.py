from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "error": "bold red",
        # Unused for now but potentially useful.
        # "command": "cyan",
        # "warning": "magenta",
    }
)

console = Console(theme=custom_theme)
