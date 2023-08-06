import traceback

from django.apps import apps
from django.core.management.base import BaseCommand

from urlid_graph.log import IndexObjectsLogger
from urlid_graph.models import ObjectModelMixin, ObjectRepository


class Command(BaseCommand):
    help = "Index objects from a specific model"

    def add_arguments(self, parser):
        parser.add_argument("--start-id", type=int, default=1)
        parser.add_argument("--batch-size", type=int, default=100_000)
        parser.add_argument("app_name")
        parser.add_argument("model")

    def handle(self, *args, **options):
        app_name = options["app_name"]
        model = options["model"]
        Model = apps.get_model(app_name, model)
        if not issubclass(Model, ObjectModelMixin):
            raise ValueError("Model '{}' doesn't inherit from `ObjectModelMixin`".format(model))

        self.logger = IndexObjectsLogger(description=f"{app_name}.{model}")
        print(f"Starting job {self.logger.job.id}")

        ok = True
        try:
            self.logger.start_step("delete-objects")
            result = ObjectRepository.objects.filter(entity_id=Model._meta.entity_uuid).delete()
            self.logger.finish_step("delete-objects", message=f"{result[0]} objects deleted")

            self.logger.start_step("index")
            ObjectRepository.objects.index(
                Model,
                start_id=options["start_id"],
                batch_size=options["batch_size"],
                callback=self.logger.progress,
            )
            self.logger.finish_step("index")

        except:  # noqa
            self.logger.error(traceback.format_exc())
            ok = False

        else:
            self.logger.finish()

        return str(ok)  # Used by import_data when calling this command programatically
