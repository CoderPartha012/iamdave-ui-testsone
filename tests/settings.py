"""Runtime settings. Override with environment variables; nothing is hardcoded to one machine."""

import os

# Trailing slash is stripped so paths can be joined consistently.
BASE_URL = os.getenv("BASE_URL", "https://www.iamdave.ai").rstrip("/")

# Seconds for an element or URL to appear before a test fails.
EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "25"))
