import psycopg2
from django.apps import apps
from django.core.management.base import BaseCommand

from urlid_graph import settings as urlid_graph_settings
from urlid_graph.log import RemoveDuplicateObjectsLogger
from urlid_graph.utils import remove_duplicates_sql


class Command(BaseCommand):
    help = "Remove duplicates for an object table"

    def add_arguments(self, parser):
        parser.add_argument("--disable-autovacuum", action="store_true")
        parser.add_argument("--disable-indexes", action="store_true")
        parser.add_argument("app_name")
        parser.add_argument("model")

    def handle(self, *args, **options):
        disable_autovacuum = options["disable_autovacuum"]
        disable_indexes = options["disable_indexes"]
        app_name = options["app_name"]
        model = options["model"]
        Model = apps.get_model(app_name, model)

        self.logger = RemoveDuplicateObjectsLogger(description=f"{app_name}.{model}")
        print(f"Starting job {self.logger.job.id}")

        connection = psycopg2.connect(urlid_graph_settings.DJANGO_DATABASE_URL)
        connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            self.logger.start_step("execute-query")
            queries = remove_duplicates_sql(
                table_name=Model._meta.db_table,
                field_names=[field.name for field in Model._meta.fields if field.name != "id"],
                disable_autovacuum=disable_autovacuum,
                disable_indexes=disable_indexes,
                disable_sync_commit=True,
                disable_triggers=True,
            )
            for counter, query in enumerate(queries, start=1):
                self.logger.progress(done=counter, total=len(queries))
                cursor.execute(query)
            self.logger.finish()
