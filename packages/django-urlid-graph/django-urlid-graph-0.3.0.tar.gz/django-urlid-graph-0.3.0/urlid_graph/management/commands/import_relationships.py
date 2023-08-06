import textwrap
import traceback
from collections import OrderedDict
from pathlib import Path

import rows
from django.core.management.base import BaseCommand
from django.db import connections
from psycopg2.sql import SQL, Identifier

import urlid_graph.settings as urlid_graph_settings
from urlid_graph.log import ImportRelationshipsLogger
from urlid_graph.utils import DatabaseConnection, random_name, read_total_size


class Command(BaseCommand):
    help = "Import relations to graph database"

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=10000)
        parser.add_argument("--chunk-size", type=int, default=8388608)
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--disable-autovacuum", action="store_true")
        parser.add_argument("--no-drop-table", action="store_true")
        parser.add_argument("--sample-size", type=int, default=3000)
        parser.add_argument("relationship")
        parser.add_argument("input_filename")

    def handle(self, *args, **options):
        debug = options.get("debug", False)
        disable_autovacuum = options["disable_autovacuum"]
        relationship = options.pop("relationship")
        input_filename = options.pop("input_filename")

        django_connection = connections[urlid_graph_settings.GRAPH_DATABASE]
        django_connection.connect()
        self.db = DatabaseConnection(connection=django_connection.connection, debug=debug)
        # TODO: `.lower()` is needed so rows' slug won't mess with the name
        temp_table_name = "tmp_" + random_name().lower()

        self.logger = ImportRelationshipsLogger(description=f"{Path(input_filename).name} -> {relationship}")
        print(f"Starting job {self.logger.job.id}")

        ok = True
        try:
            with self.logger.step("pre-import", message_start="Preparing table to import"):
                self.logger.message("Disabling sync commit")
                self.db.disable_sync_commit()

                if disable_autovacuum:
                    self.logger.message(f"Disabling autovacuum for {table_name}")
                    self.db.disable_autovacuum()

            try:
                self.execute_import_data(relationship, input_filename, temp_table_name, *args, **options)
            except:  # noqa
                self.logger.error(traceback.format_exc())
                ok = False

            for relname in (
                f"{urlid_graph_settings.GRAPH_NAME}.ag_vertex",
                f"{urlid_graph_settings.GRAPH_NAME}.ag_edge",
            ):
                self.logger.message(f"Running VACUUM ANALYZE on {relname}")
                self.db.vacuum_analyze(relname)

        except:  # noqa
            self.logger.error(traceback.format_exc())
            ok = False

        finally:
            with self.logger.step("post-import"):
                if disable_autovacuum:
                    self.logger.message(f"Enabling autovacuum for {table_name}")
                    self.db.enable_autovacuum()
                self.logger.message("Enabling sync commit")
                self.db.enable_sync_commit()

        self.logger.finish()
        return str(ok)  # Used by import_data when calling this command programatically

    def create_properties(self, header, type_):
        # TODO: use `rows.properties.{field}` instead
        props = []
        for field in header:
            props.append(f"ON {type_.upper()} SET r.{field} = row.{field}")

        return "\r\n".join(props)

    def create_merge_query(self, schema, relation_name, temp_table_name):
        header = [field_name for field_name in schema.keys() if field_name != "id" and "node_uuid" not in field_name]
        props_create = self.create_properties(header, type_="create")
        props_match = self.create_properties(header, type_="match")
        # https://neo4j.com/developer/kb/understanding-how-merge-works/

        # TODO: may create a VLABEL for each entity and import the objects
        # using this VLABEL (not `object`) - it may not be possible depending
        # on the extraction file format.
        return textwrap.dedent(
            """
            LOAD FROM {temp_table_name} as row
            WITH row WHERE $1 < row.id AND row.id <= $2
            MERGE (obj1:object {{uuid: row.from_node_uuid}})
            MERGE (obj2:object {{uuid: row.to_node_uuid}})
            MERGE (obj1)-[r:{relation}]->(obj2)
            {create}
            {match}
            """.format(
                relation=relation_name,
                temp_table_name=temp_table_name,
                create=props_create,
                match=props_match,
            )
        )

    def create_table(self, schema, table_name):
        # Create table manually so we can inject an `id` column to control the
        # batch import data.

        schema = schema.copy()  # Do not change original object
        schema["id"] = rows.fields.IntegerField
        sql = rows.utils.pg_create_table_sql(schema, table_name=table_name, unlogged=True)
        # TODO: change the way we change this behavior (serial)
        sql = sql.replace('"id" BIGINT', '"id" SERIAL').replace("id BIGINT", "id SERIAL")
        self.db.execute_query(sql)

    def optimize_data_table(self, table_name):
        self.db.execute_queries(
            [
                f"ALTER TABLE {table_name} ADD PRIMARY KEY (id)",
                f"VACUUM ANALYZE {table_name}",
            ],
        )

    def ensure_graph_requisites(self, relation_name):
        self.db.execute_query(
            SQL("CREATE ELABEL IF NOT EXISTS {}").format(Identifier(relation_name)),
        )
        self.db.execute_query(
            SQL("CREATE VLABEL IF NOT EXISTS {}").format(Identifier("object")),
        )
        self.db.execute_query(
            SQL("CREATE PROPERTY INDEX IF NOT EXISTS idx_vlabel_object_uuid ON object (uuid)"),
        )

    def import_relations(self, schema, relation_name, temp_table_name, n_rows, batch_size):
        cypher_statement = self.create_merge_query(schema, relation_name, temp_table_name)
        statement_name = f"urlid_tmp_rel_{random_name(10)}"
        self.db.execute_query(f"PREPARE {statement_name}(int, int) AS {cypher_statement}")
        for min_id in range(0, n_rows + 1, batch_size):
            self.db.execute_query(f"EXECUTE {statement_name} ({min_id}, {min_id + batch_size})")
            self.logger.progress(done=min(min_id + batch_size, n_rows), total=n_rows)
        self.db.execute_query(f"DEALLOCATE {statement_name}")

    def execute_import_data(self, relation_name, input_filename, temp_table_name, *args, **options):
        self.logger.start_step("import-table-data")
        self.logger.message(f"Creating table {temp_table_name}")
        schema = OrderedDict(
            [
                ("from_node_uuid", rows.fields.UUIDField),
                ("to_node_uuid", rows.fields.UUIDField),
                ("relationship", rows.fields.TextField),
                ("properties", rows.fields.JSONField),
            ]
        )
        self.create_table(schema, temp_table_name)
        file_size = read_total_size(input_filename)

        def update_progress(done, total):
            # done is actually the last step done and total the total_done
            self.logger.progress(done=total, total=file_size)

        self.logger.message("Importing data")
        rows_ouput = rows.utils.pgimport(
            input_filename,
            encoding="utf-8",
            dialect="excel",
            table_name=temp_table_name,
            create_table=False,
            database_uri=urlid_graph_settings.GRAPH_DATABASE_URL,
            schema=schema,
            callback=update_progress,
            chunk_size=options["chunk_size"],
        )
        total_imported, batch_size = rows_ouput["rows_imported"], options["batch_size"]
        self.logger.message(f"Imported {total_imported} rows to '{temp_table_name}'")

        self.logger.message("Optimizing table for reading")
        self.optimize_data_table(temp_table_name)
        self.logger.finish_step("import-table-data")

        self.logger.start_step("import-relationships")
        self.logger.message(f"Ensuring elabel {relation_name} exists")
        self.ensure_graph_requisites(relation_name)

        self.import_relations(schema, relation_name, temp_table_name, total_imported, batch_size)

        if not options["no_drop_table"]:
            self.logger.message(f"Deleting table '{temp_table_name}'")
            self.db.delete_table(temp_table_name)
        self.logger.finish_step("import-relationships")
