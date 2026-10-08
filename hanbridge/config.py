"""Configuration for HanBridge AI.

All secrets come from environment variables — never hardcode keys.
Get a Nebius Token Factory API key at https://tokenfactory.nebius.com/
(New accounts receive free promotional credits; hackathon builders can also
use the Devpost resources page code for extra credits.)
"""

import os

NEBIUS_BASE_URL = os.getenv(
    "NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"
)
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY", "")
NEBIUS_MODEL = os.getenv("NEBIUS_MODEL", "")

# Substrings (lowercase) used to prefer NVIDIA models when auto-selecting.
NVIDIA_HINTS = ("nemotron", "nvidia")
