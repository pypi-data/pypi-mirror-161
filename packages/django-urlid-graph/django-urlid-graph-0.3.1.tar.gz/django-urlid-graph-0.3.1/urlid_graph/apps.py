from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import DataError
from django.db.backends.signals import connection_created

from urlid_graph import settings as urlid_graph_settings


def set_graph_path(sender, connection, **kwargs):
    graph_name = urlid_graph_settings.GRAPH_NAME
    if graph_name and connection.alias == urlid_graph_settings.GRAPH_DATABASE:
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"SET graph_path = {graph_name}")
            except DataError:
                cursor.execute(f"CREATE graph {graph_name}")
                cursor.execute(f"SET graph_path = {graph_name}")


class DataGraphConfig(AppConfig):
    name = "urlid_graph"

    def ready(self):
        if urlid_graph_settings.TESTING_ENV:
            # TESTING_ENV is used so projects which depends on this app can run
            # the tests without configuring everything needed by this app (like
            # a graph database).
            return

        urlid_graph_db_router = "urlid_graph.db_router.RelationAndGraphDBRouter"
        if "rest_framework" not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("rest_framework must be in installed apps.")
        if getattr(settings, "GRAPH_DATABASE", None) is None:
            raise ImproperlyConfigured("must set a value for GRAPH_DATABASE in settings.py")
        if getattr(settings, "GRAPH_DATABASE_URL", None) is None:
            raise ImproperlyConfigured("must set a value for GRAPH_DATABASE_URL in settings.py")
        if settings.GRAPH_DATABASE not in settings.DATABASES:
            raise ImproperlyConfigured("must set GRAPH_DATABASE with GRAPH_DATABASE_URL in DATABASES")
        if urlid_graph_db_router not in settings.DATABASE_ROUTERS:
            raise ImproperlyConfigured(f"must set {urlid_graph_db_router} in DATABASE_ROUTERS")

        connection_created.connect(set_graph_path)
