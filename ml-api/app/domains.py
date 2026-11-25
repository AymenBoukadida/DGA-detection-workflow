from __future__ import annotations

import re
from urllib.parse import urlsplit

_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def normalize_domain(raw: str) -> str:
    if not isinstance(raw, str):
        raise ValueError("domain must be a string")
    value = raw.strip()
    if not value:
        raise ValueError("domain is empty")
    if any(char.isspace() for char in value):
        raise ValueError("domain must not contain whitespace")

    if "://" in value:
        try:
            host = urlsplit(value).hostname
        except ValueError as exc:
            raise ValueError("domain is not a valid URL") from exc
        if not host:
            raise ValueError("domain has no host")
        value = host
    else:
        value = value.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
        if "@" in value:
            value = value.rsplit("@", 1)[1]
        if ":" in value:
            host, _, port = value.partition(":")
            if not port.isdigit():
                raise ValueError("domain has an invalid port")
            value = host

    value = value.lower().rstrip(".")
    if not value:
        raise ValueError("domain is empty")
    if len(value) > 253:
        raise ValueError("domain is longer than 253 characters")

    labels = value.split(".")
    if len(labels) < 2:
        raise ValueError("domain must contain at least two labels")
    if any(not label for label in labels):
        raise ValueError("domain contains an empty label")
    if any(len(label) > 63 for label in labels):
        raise ValueError("domain label is longer than 63 characters")
    if not all(_LABEL_RE.fullmatch(label) for label in labels):
        raise ValueError("domain contains invalid characters")
    if len(labels[-1]) < 2 or labels[-1].isdigit():
        raise ValueError("domain has an invalid top-level label")
    return value
