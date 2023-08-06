import traceback
from pathlib import Path

import rows
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connections

import urlid_graph.settings as urlid_graph_settings
from urlid_graph.log import ImportObjectsLogger
from urlid_graph.models import DatasetModel, ObjectModelMixin, ObjectRepository, get_urlid_database_uri
from urlid_graph.utils import DatabaseConnection, read_total_size


class Command(BaseCommand):
    help = "Import objects into the correct model"

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=100_000, help="Number of rows to index per turn")
        parser.add_argument(
            "--chunk-size", type=int, default=8_388_608, help="Chunk size used to read CSV file while importing data"
        )
        parser.add_argument("--disable-autovacuum", action="store_true")
        parser.add_argument("--disable-indexes", action="store_true")
        parser.add_argument("app_name")
        parser.add_argument("model")
        parser.add_argument("input_filename")

    def handle(self, *args, **options):
        app_name = options["app_name"]
        model = options["model"]
        input_filename = options["input_filename"]
        batch_size = options["batch_size"]
        chunk_size = options["chunk_size"]
        disable_autovacuum = options["disable_autovacuum"]
        disable_indexes = options["disable_indexes"]

        Model = apps.get_model(app_name, model)
        if not issubclass(Model, (DatasetModel, ObjectModelMixin)):
            raise ValueError("Model '{}' doesn't inherit from `ObjectModelMixin` or `DatasetModel`".format(model))
        table_name = Model._meta.db_table
        connection = connections[urlid_graph_settings.DJANGO_DATABASE]
        db = DatabaseConnection(connection=connection)

        self.logger = ImportObjectsLogger(description=f"{Path(input_filename).name} -> {app_name}.{model}")
        print(f"Starting job {self.logger.job.id}")

        ok = True
        try:
            with self.logger.step("pre-import", message_start="Preparing table to import"):
                self.logger.message("Disabling sync commit")
                db.disable_sync_commit()

                if disable_autovacuum:
                    self.logger.message(f"Disabling autovacuum for {table_name}")
                    db.disable_autovacuum(table_name)

                if disable_indexes:
                    self.logger.message(f"Disabling table indexes for {table_name}")
                    db.execute_query(
                        f"UPDATE pg_index SET indisready = FALSE WHERE indrelid = '{table_name}'::regclass"
                    )

                self.logger.message(f"Disabling triggers for {table_name}")
                db.execute_query(f'ALTER TABLE "{table_name}" DISABLE TRIGGER ALL')

            last_object = Model.objects.order_by("-id").first()
            start_id = last_object.id + 1 if last_object is not None else None
            self.import_data(input_filename, chunk_size, table_name)

            if issubclass(Model, ObjectModelMixin):
                # Don't need to add to search index if it's just a custom
                # dataset
                self.add_to_search_index(Model, start_id, batch_size)

        except:  # noqa
            self.logger.error(traceback.format_exc())
            ok = False

        finally:
            with self.logger.step("post-import"):
                if disable_indexes:
                    self.logger.message(f"Reindexing table {table_name}")
                    db.execute_query(f'REINDEX TABLE "{table_name}"')

                self.logger.message(f"Reenabling triggers on {table_name}")
                db.execute_query(f'ALTER TABLE "{table_name}" ENABLE TRIGGER ALL')

                self.logger.message(f"Running VACUUM ANALYZE on {table_name}")
                db.vacuum_analyze(table_name)

                if disable_autovacuum:
                    self.logger.message(f"Enabling autovacuum for {table_name}")
                    db.enable_autovacuum(table_name)

                self.logger.message("Enabling sync commit")
                db.enable_sync_commit()

        self.logger.finish()
        return str(ok)  # Used by import_data when calling this command programatically

    def import_data(self, input_filename, chunk_size, table_name):
        self.logger.start_step("import")
        file_size = read_total_size(input_filename)

        def update_progress(done, total):
            # done is actually the last step done and total the total_done
            self.logger.progress(done=total, total=file_size)

        try:
            rows_output = rows.utils.pgimport(
                input_filename,
                encoding="utf-8",
                dialect="excel",
                table_name=table_name,
                database_uri=get_urlid_database_uri(),
                create_table=False,
                chunk_size=chunk_size,
                callback=update_progress,
            )
        except RuntimeError:
            self.logger.error(traceback.format_exc())
            raise
        else:
            self.logger.finish_step("import", message=f"Imported {rows_output['rows_imported']} rows to '{table_name}'")

    def add_to_search_index(self, Model, start_id, batch_size):
        self.logger.start_step("index", message=f"start_id: {start_id}, batch_size: {batch_size}")

        ObjectRepository.objects.index(
            Model,
            start_id=start_id,
            batch_size=batch_size,
            callback=self.logger.progress,
        )
        self.logger.finish_step("index")
