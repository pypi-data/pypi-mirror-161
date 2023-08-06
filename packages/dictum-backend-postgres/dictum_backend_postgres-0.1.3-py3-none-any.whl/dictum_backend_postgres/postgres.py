from typing import Optional

from dictum_core.backends.mixins.datediff import DatediffCompilerMixin
from dictum_core.backends.sql_alchemy import SQLAlchemyBackend, SQLAlchemyCompiler
from sqlalchemy import Float, Integer
from sqlalchemy.sql import cast


class PostgresCompiler(DatediffCompilerMixin, SQLAlchemyCompiler):
    def div(self, a, b):
        """Dictum's division is like Python's, e.g. 1/2 == 0.5,
        while in Postgres 1/2 == 0, so we need to cast the first
        arg to float.
        """
        return cast(a, Float) / b

    def datepart(self, part, arg):
        # cast cause date_part returns double
        return cast(super().datepart(part, arg), Integer)

    def datediff_day(self, start, end):
        return self.todate(end) - self.todate(start)


class PostgresBackend(SQLAlchemyBackend):
    type = "postgres"
    compiler_cls = PostgresCompiler

    def __init__(
        self,
        database: str = "postgres",
        host: str = "localhost",
        port: int = 5432,
        username: str = "postgres",
        password: Optional[str] = None,
        pool_size: Optional[int] = 5,
        default_schema: Optional[str] = None,
    ):
        super().__init__(
            drivername="postgresql",
            database=database,
            host=host,
            port=port,
            username=username,
            password=password,
            pool_size=pool_size,
            default_schema=default_schema,
        )
