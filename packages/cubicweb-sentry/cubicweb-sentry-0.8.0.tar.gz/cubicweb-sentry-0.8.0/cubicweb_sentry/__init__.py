import logging
import optparse

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

try:
    import pyramid  # noqa
except ImportError:
    HAS_PYRAMID = False
else:
    HAS_PYRAMID = True
    from sentry_sdk.integrations.pyramid import PyramidIntegration


def init_sdk(cwconfig):
    """Initialize `sentry_sdk` from cubicweb configuration."""
    try:
        dsn = cwconfig["sentry-dsn"]
    except (optparse.OptionError, KeyError):
        return
    if not dsn:
        return
    release = cwconfig.cube_version(cwconfig.cubes()[0])
    log_level = cwconfig["sentry-log-level"]
    integrations = []
    if HAS_PYRAMID:
        integrations.append(PyramidIntegration())
    if log_level is not None:
        integrations.append(
            LoggingIntegration(
                level=logging.DEBUG,  # Capture debug and above as breadcrumbs
                event_level=log_level.upper(),
            )
        )
    sentry_sdk.init(
        dsn=dsn,
        release=release,
        integrations=integrations,
        environment=cwconfig["sentry-environment"],
    )
    return sentry_sdk
