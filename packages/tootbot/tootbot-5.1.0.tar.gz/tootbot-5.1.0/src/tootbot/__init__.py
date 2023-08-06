"""Package 'tootbot' level definitions."""
import sys

from typing_extensions import Final

CODE_VERSION_MAJOR: Final[int] = 5  # Current major version of this code
CODE_VERSION_MINOR: Final[int] = 1  # Current minor version of this code
CODE_VERSION_PATCH: Final[int] = 0  # Current patch version of this code

__version__: Final[
    str
] = f"{CODE_VERSION_MAJOR}.{CODE_VERSION_MINOR}.{CODE_VERSION_PATCH}"
__package_name__: Final[str] = "tootbot"

# Package level Static Variables
POST_RECORDER_CSV_FILE: Final[str] = "cache.csv"
POST_RECORDER_SQLITE_DB: Final[str] = "history.db"
USER_AGENT: Final[
    str
] = f"Tootbot_v{__version__}_(https://pypi.org/project/tootbot/)_Python_{sys.version.split()[0]}"
PROGRESS_BAR_FORMAT: Final[str] = "{desc}: {percentage:3.0f}%|{bar}| Eta: {remaining}"
