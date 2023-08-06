import bmo.version

__version__ = bmo.version.__version__

import logging
import os

LOGLEVEL = os.environ.get("BMO_LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)

import sentry_sdk

from sentry_sdk.integrations.logging import LoggingIntegration

# All of this is already happening by default!
sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.WARNING,  # Send warning/error as events
)

sentry_sdk.init(
    dsn="https://fbef4a361df84b5db0a4b27179c41280@traces.subcom.link/5",
    integrations=[sentry_logging],
    traces_sample_rate=0.5,
)
