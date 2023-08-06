import agensgraph  # noqa
from django.conf import settings

USER_SETTINGS = getattr(settings, "URLID_GRAPH", dict())

DEFAULTS = {
    "SEARCH_LANGUAGE": "pg_catalog.portuguese",
    "RELATIONSHIP_DEPTH_LIMIT": 3,
    "ALL_NODES_RELATIONSHIPS_CHUNK_SIZE": 10,
    "GRAPH_NAME": "graph_db",
    "NODES_CSV_SIZE_LIMIT": 1000,
}


def get_settings(key):
    return USER_SETTINGS.get(key, DEFAULTS[key])


SEARCH_LANGUAGE = get_settings("SEARCH_LANGUAGE")
RELATIONSHIP_DEPTH_LIMIT = get_settings("RELATIONSHIP_DEPTH_LIMIT")
ALL_NODES_RELATIONSHIPS_CHUNK_SIZE = get_settings("ALL_NODES_RELATIONSHIPS_CHUNK_SIZE")
GRAPH_NAME = get_settings("GRAPH_NAME")
NODES_CSV_SIZE_LIMIT = get_settings("NODES_CSV_SIZE_LIMIT")

DJANGO_DATABASE_URL = settings.DATABASE_URL
DJANGO_DATABASE = "default"
GRAPH_DATABASE = getattr(settings, "GRAPH_DATABASE", None)
GRAPH_DATABASE_URL = getattr(settings, "GRAPH_DATABASE_URL", None)

TESTING_ENV = getattr(settings, "TESTING_ENV", False)
