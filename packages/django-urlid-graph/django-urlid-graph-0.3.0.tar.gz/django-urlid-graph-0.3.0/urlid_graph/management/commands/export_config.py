import json

import rows
from django.core.management.base import BaseCommand

from urlid_graph.models import ElementConfig


class Command(BaseCommand):
    help = "Export elements' configurations"

    def add_arguments(self, parser):
        parser.add_argument("output_filename")

    def handle(self, *args, **options):
        writer = rows.utils.CsvLazyDictWriter(options["output_filename"])
        for element in ElementConfig.objects.all().iterator():
            writer.writerow(
                {
                    key: value if key != "data" else json.dumps(value)
                    for key, value in element.__dict__.items()
                    if key != "_state"
                }
            )
        writer.close()
