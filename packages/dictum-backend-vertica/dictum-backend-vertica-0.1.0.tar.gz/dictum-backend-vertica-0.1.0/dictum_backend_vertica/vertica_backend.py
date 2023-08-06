from typing import Optional

from dictum_core.backends.sql_alchemy import SQLAlchemyBackend, SQLAlchemyCompiler
from sqlalchemy import Integer, cast


class VerticaCompiler(SQLAlchemyCompiler):
    """Vertica implements datediff, but weeks start on Sunday."""

    def datepart(self, part, arg):
        """Datepart returns a float."""
        if part == "week":
            part = "isoweek"
        expr = super().datepart(part, arg)
        return cast(expr, Integer)

    def datediff(self, part, start, end):
        """Vertica's datediff only works with Sunday-based weeks, Dictum's weeks are
        Monday-based, so we need to override this for weeks.
        """
        if part == "week":
            # interestingly, date_trunc uses ISO weeks starting on Monday
            return self.tointeger(
                self.datediff(
                    "day", self.datetrunc("week", start), self.datetrunc("week", end)
                )
                / 7
            )
        return super().datediff(part, start, end)


class VerticaBackend(SQLAlchemyBackend):
    type = "vertica"
    compiler_cls = VerticaCompiler

    # TODO: support_statement_cache warning

    def __init__(
        self,
        database: str,
        host: str = "localhost",
        port: int = 5433,
        username: str = "dbadmin",
        password: Optional[str] = None,
        pool_size: Optional[int] = 5,
        default_schema: Optional[str] = None,
    ):
        super().__init__(
            drivername="vertica+vertica_python",
            database=database,
            host=host,
            port=port,
            username=username,
            password=password,
            pool_size=pool_size,
            default_schema=default_schema,
        )
