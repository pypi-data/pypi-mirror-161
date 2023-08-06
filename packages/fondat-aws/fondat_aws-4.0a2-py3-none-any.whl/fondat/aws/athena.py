"""..."""

import fondat.sql

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fondat.sql import Expression
from typing import Any


class Database:
    """..."""

    pass


class Table:
    """..."""

    def __init__(
        database: Database,
        name: str,
        columns: None,
        partitioned_by: list[str],
        location: str,
        properties: dict[str, str],
    ):
        pass


def athena_database_resource(config: Any) -> Any:
    pass
