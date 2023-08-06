import urlid_graph.settings as urlid_graph_settings


class RelationAndGraphDBRouter:
    def db_for_read(self, model, **hints):
        return "default"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if "target_db" in hints:
            return db == urlid_graph_settings.GRAPH_DATABASE
        return db == "default"
