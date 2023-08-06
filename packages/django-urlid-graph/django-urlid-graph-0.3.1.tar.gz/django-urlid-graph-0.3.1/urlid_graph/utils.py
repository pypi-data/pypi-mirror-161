import datetime
import pprint
import random
import string
import textwrap
import time
from contextlib import contextmanager
from itertools import zip_longest
from textwrap import dedent

import psycopg2
from rows.utils import uncompressed_size


def random_name(n=16):
    return "".join(random.choice(string.ascii_letters) for _ in range(n))


@contextmanager
def working(message, finish="done in {duration}."):
    print(f"{message}... ", flush=True, end="")
    start = time.time()
    yield
    end = time.time()
    print(finish.format(duration=datetime.timedelta(seconds=end - start)))


def read_total_size(source):
    try:
        total_size = uncompressed_size(source)
    except (RuntimeError, ValueError):
        total_size = None

    return total_size


class DatabaseConnection:

    # TODO: move `working` logic to a logger with different levels

    def __init__(self, uri=None, connection=None, debug=False):
        if (not uri and not connection) or (uri and connection):
            raise ValueError("Only one parameter (uri or connection) must be specified")
        self._connection = connection
        self._uri = uri
        self.debug = debug

    @property
    def connection(self):
        if not self._connection:
            self._connection = psycopg2.connect(self._uri)

        return self._connection

    def debug_message(self, query, params):
        if not isinstance(query, str):  # psycopg2.sql.SQL instance
            query = query.as_string(self.connection)
        output = []
        for line in textwrap.dedent(query).strip().splitlines():
            output.extend(textwrap.wrap(line, 80))
        query_text = textwrap.indent("\n".join(output), "*  ")

        message = f"\n* Executing query:\n{query_text}\n"
        if params is not None:
            params_text = textwrap.indent(pprint.pformat(params), "*  ")
            message += f"* with params:\n{params_text}\n"
        return message

    def execute_query(self, query, params=None):
        with self.connection.cursor() as cursor:
            if self.debug:
                with working(self.debug_message(query, params)):
                    cursor.execute(query, params)
            else:
                cursor.execute(query, params)
            return cursor

    def execute_queries(self, queries, params_list=None):
        params_list = params_list or []
        with self.connection.cursor() as cursor:
            for query, params in zip_longest(queries, params_list):
                if self.debug:
                    with working(self.debug_message(query, params)):
                        cursor.execute(query, params)
                else:
                    cursor.execute(query, params)
            return cursor

    def enable_trigger(self, table_name, trigger):
        return self.execute_query(f"ALTER TABLE {table_name} ENABLE TRIGGER {trigger}")

    def disable_trigger(self, table_name, trigger):
        return self.execute_query(f"ALTER TABLE {table_name} DISABLE TRIGGER {trigger}")

    def disable_sync_commit(self):
        return self.execute_query("SET synchronous_commit = off")

    def enable_sync_commit(self):
        return self.execute_query("SET synchronous_commit = on")

    def enable_autovacuum(self, table_name=None):
        if table_name is not None:
            queries = [f"ALTER TABLE {table_name} SET (autovacuum_enabled = true)"]
        else:  # Enable for the whole database
            queries = [
                "ALTER SYSTEM SET autovacuum = on",
                "SELECT pg_reload_conf()",
            ]
        return self.execute_queries(queries)

    def disable_autovacuum(self, table_name=None):
        if table_name is not None:
            queries = [f"ALTER TABLE {table_name} SET (autovacuum_enabled = false)"]
        else:  # Disable for the whole database
            queries = [
                "ALTER SYSTEM SET autovacuum = off",
                "SELECT pg_reload_conf()",
            ]
        return self.execute_queries(queries)

    def vacuum_analyze(self, table_name=None):
        return self.execute_query(f"VACUUM ANALYZE {table_name or ''}")

    def delete_table(self, table_name):
        self.execute_query(f"DROP TABLE {table_name}")


def remove_duplicates_sql(
    table_name,
    field_names,
    disable_autovacuum=False,
    disable_indexes=False,
    disable_sync_commit=True,
    disable_triggers=True,
):

    before, queries, after = [], [], []
    field_list = ", ".join(field_names)

    if disable_autovacuum:
        before.append(f"ALTER TABLE {table_name} SET (autovacuum_enabled = false);")

    queries.extend(
        [
            "BEGIN;",
            f"""
            CREATE TEMP TABLE {table_name}_unique ON COMMIT DROP AS
                SELECT DISTINCT
                    {field_list}
                FROM {table_name};
            """,
            f"""
            TRUNCATE TABLE {table_name};
            """,
        ]
    )
    if disable_sync_commit:
        queries.append("SET LOCAL synchronous_commit = off;")
    if disable_indexes:
        queries.append(f"UPDATE pg_index SET indisready = FALSE WHERE indrelid = '{table_name}'::regclass;")
    if disable_triggers:
        queries.append(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL;")
    queries.append(
        f"""
        INSERT INTO {table_name} ({field_list})
            SELECT {field_list} FROM {table_name}_unique;
        """
    )
    if disable_indexes:
        queries.append(f"REINDEX TABLE {table_name};")
    if disable_triggers:
        queries.append(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL;")
    if disable_sync_commit:
        queries.append("RESET synchronous_commit;")
    queries.append("END;")
    after.append(f"VACUUM ANALYZE {table_name};")

    if disable_autovacuum:
        queries.append(f"ALTER TABLE {table_name} RESET (autovacuum_enabled);")

    return [
        query
        for query in (
            "\n".join(dedent(query) for query in before),
            "\n".join(dedent(query) for query in queries),
            "\n".join(dedent(query) for query in after),
        )
        if query.strip()
    ]
