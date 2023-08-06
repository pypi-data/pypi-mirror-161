import rows
from django.core.management.base import BaseCommand

from urlid_graph.models import ElementConfig


class Command(BaseCommand):
    help = "Import entities, properties and relationships config"

    def add_arguments(self, parser):
        parser.add_argument("input_filename")

    def handle(self, *args, **options):
        config_rows = rows.import_from_csv(
            options["input_filename"],
            force_types={
                "config_type": rows.fields.IntegerField,
                "data": rows.fields.JSONField,
                "label": rows.fields.TextField,
                "name": rows.fields.TextField,
                "parent_name": rows.fields.TextField,
                "parent_type": rows.fields.IntegerField,
            },
        )

        for row in config_rows:
            cfg, created = ElementConfig.objects.update_or_create(
                config_type=row.config_type,
                name=row.name,
                parent_type=row.parent_type or None,
                parent_name=row.parent_name,
                defaults={"label": row.label, "data": row.data},
            )

            print(
                f"{'CREATED' if created else 'UPDATED'} cfg {cfg.label} para {cfg.get_config_type_display()} {cfg.name}"
            )
