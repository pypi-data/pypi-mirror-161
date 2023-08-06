from pathlib import Path

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import objects and relationships from a directory"

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--disable-autovacuum", action="store_true")
        parser.add_argument("--disable-indexes", action="store_true")
        parser.add_argument("--filetype", action="append")

    def handle(self, *args, **options):
        cmd_options = {
            "disable_autovacuum": options["disable_autovacuum"],
            "disable_indexes": options["disable_indexes"],
        }
        cmd_options_relations = {
            "disable_autovacuum": options["disable_autovacuum"],
        }
        path = Path(options["path"])
        file_types = options["filetype"]
        if not file_types:
            file_types = all
        else:
            file_types = [file_type.lower() for file_type in file_types]
            for file_type in file_types:
                if file_type not in ("object", "relationship"):
                    raise ValueError(f"Unknown value '{file_type}'")

        # Import files containing objects
        # TODO: should use ObjectModelMixin.__subclasses__() so we don't need
        # to traverse all apps/models.
        model_app = {
            model_name.lower(): app_name
            for app_name, app_models in apps.all_models.items()
            for model_name, Model in app_models.items()
        }
        if file_types is all or "object" in file_types:
            filenames = [str(filename.absolute()) for filename in path.glob("*object*.csv*")]
            oks = []
            for filename in filenames:
                model = filename.split("object")[1].split(".csv")[0].replace("-", "").replace("_", "")
                app_name = model_app[model]
                oks.append(call_command("import_objects", app_name, model, filename, **cmd_options) == "True")
            ok = all(oks)
            if not ok:
                return str(ok)

        # Import files containing relationships
        if file_types is all or "relationship" in file_types:
            oks = []
            for filename in path.glob("*relationship*.csv*"):
                relationship = filename.absolute().name.split("relationship")[1].split(".csv")[0]
                filename = str(filename.absolute())
                if relationship.startswith("-") or relationship.startswith("_"):
                    relationship = relationship[1:]
                if relationship.endswith("-") or relationship.endswith("_"):
                    relationship = relationship[:-1]

                oks.append(
                    call_command("import_relationships", relationship, filename, **cmd_options_relations) == "True"
                )
            ok = all(oks)
            if not ok:
                return str(ok)

        return "True"
