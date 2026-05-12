"""Validation helper functions."""

from __future__ import annotations

import re


PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def is_valid_project_name(value: str) -> bool:
    return bool(PROJECT_NAME_PATTERN.fullmatch(value))


def parse_hex_address(value: str) -> int:
    return int(value, 16)
