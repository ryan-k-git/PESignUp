from typing import Optional
from pathlib import Path
import aiosqlite

from global_src.constants import SCHEMA_PATH, DATABASE_PATH


class Database:
    def __init__(self, path: str | Path=DATABASE_PATH, schema_path: str | Path=SCHEMA_PATH) -> None:
        self.path = path
        self.schema_path = schema_path
        self.con: Optional[aiosqlite.Connection] = None

    async def _create_tables(self, schema_path: str | Path=SCHEMA_PATH) -> None:
        """
        Creates tables in the database based on the schema in the schema path.
        :param schema_path: path to the schema file
        :return: None
        """
        con = self.con
        with open(schema_path, "r", encoding='utf-8') as f:
            schema = f.read()
        await con.executescript(schema)
        await con.commit()

    async def _get_con(self):
        if not self.con:
            self.con = await aiosqlite.connect(self.path)
        return self.con

    async def fetch_one(self, query: str, values: tuple=None) -> tuple:
        """
        Fetches one row of the database based on the query and the values
        :param query: query to fetch
        :param values: values from query
        :return: tuple
        """
        con = await self._get_con()
        if values:
            async with con.execute(query, values) as cur:
                data = await cur.fetchone()
        else:
            async with con.execute(query) as cur:
                data = await cur.fetchone()
        return data

    async def fetch_all(self, query: str, values: tuple = None) -> list[tuple]:
        """
        fetches all rows of the database based on the query and the values
        :param query: query to fetch
        :param values: values from query
        :return: list[tuple]
        """
        con = await self._get_con()
        if values:
            async with con.execute(query, values) as cur:
                data = await cur.fetchall()
        else:
            async with con.execute(query) as cur:
                data = await cur.fetchall()
        return data

    async def execute(self, query: str, values: tuple = None, commit=True) -> None:
        """
        Execute an SQL query in the database based on the query and the values
        :param query: query to execute
        :param values: values from query
        :param commit: whether to commit the query
        :return: None
        """
        con = await self._get_con()
        await con.execute(query, values)
        if commit:
            await con.commit()

    async def executescript(self, query: str) -> None:
        """
        execute an SQL script
        :param query: query to execute
        :return: None
        """
        con = await self._get_con()
        await con.executescript(query)
        await con.commit()

    async def commit(self) -> None:
        """
        commit to the database
        :return: None
        """
        con = await self._get_con()
        await con.commit()

    async def initialize(self) -> None:
        """
        initialize the database
        :return: None
        """
        await self._get_con()
        await self._create_tables(self.schema_path)

DATABASE = Database()