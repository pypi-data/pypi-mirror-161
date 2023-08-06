options = (
    (
        "sentry-dsn",
        {
            "type": "string",
            "default": "",
            "help": "Sentry DSN (eg. https://public_key:secret_key@sentry.local/project_id?timeout=10 )",  # noqa: E501
            "group": "sentry",
            "level": 5,
        },
    ),
    (
        "sentry-public-dsn",
        {
            "type": "string",
            "default": "",
            "help": "Sentry Public DSN (eg. https://token@sentry.local/project_id )",
            "group": "sentry",
            "level": 5,
        },
    ),
    (
        "sentry-log-level",
        {
            "type": "choice",
            "choices": ("error", "critical"),
            "default": None,
            "help": "emit Sentry event when logging exception with choosen log level (disabled by default)",  # noqa: E501
            "group": "sentry",
            "level": 5,
        },
    ),
    (
        "sentry-environment",
        {
            "type": "string",
            "default": None,
            "help": "Sentry Application Environment (eg: prod, preprod, demo)",
            "group": "sentry",
            "level": 5,
        },
    ),
)
