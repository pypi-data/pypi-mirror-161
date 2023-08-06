from contextlib import contextmanager
from dataclasses import dataclass

from urlid_graph.models import JobLog, LogStep


@dataclass
class Step:
    slug: str
    description: str


class AsyncLogger:
    name: str = None
    steps: list = None

    def __init__(self, description):
        self.description = description
        self.job = self._init_job()
        self._current_step = None

        if self.name is None:
            raise ValueError("Attribute 'name' cannot be None")

        if self.steps is None:
            raise ValueError("Attribute 'steps' cannot be None")

        self._step_slugs = [s.slug for s in self.steps]

    def _init_job(self):
        return JobLog.objects.create(name=self.name, description=self.description)

    def start_step(self, step, message=None):
        if step not in self._step_slugs:
            raise ValueError(f"Step '{step}' not found")

        if self._current_step is not None:
            self.finish_step(self._current_step, force=True)

        LogStep.objects.create(job=self.job, step=step, action="start-step", message=message)
        self._current_step = step

    def progress(self, done, total, message=None):
        if self._current_step is None:
            raise ValueError(f"Cannot make progress in a job which current step is None")

        LogStep.objects.create(
            job=self.job, step=self._current_step, action="progress", done=done, total=total, message=message
        )

    def finish_step(self, step, message=None, force=False):
        if step not in self._step_slugs:
            raise ValueError(f"Step '{step}' not found")

        if not force and (self._current_step is None or self._current_step != step):
            raise ValueError(f"Current step different from '{self._current_step}'")

        LogStep.objects.create(job=self.job, step=step, action="finish-step", message=message)
        self._current_step = None

    def message(self, message):
        current_step = self._current_step or "no-step"
        LogStep.objects.create(job=self.job, step=current_step, action="message", message=message)

    def error(self, message):
        current_step = self._current_step or "no-step"
        LogStep.objects.create(job=self.job, step=current_step, action="error", message=message)

    def finish(self, message=None):
        if self._current_step is not None:
            self.finish_step(self._current_step, force=True)

        LogStep.objects.create(job=self.job, step="complete", action="finish", message=message)

    def __str__(self):
        return f"{self.name} - {self.description}: {self.job.job_id}"

    @contextmanager
    def step(self, step, message_start=None, message_finish=None):
        self.start_step(step, message=message_start)
        yield
        self.finish_step(step, message=message_finish)


class ImportObjectsLogger(AsyncLogger):
    name = "importing objects"
    steps = [
        Step("pre-import", "Disable indexes etc."),
        Step("import", "Import data into table"),
        Step("index", "Index imported objects in ObjectRepository"),
        Step("post-import", "Re-enable indexes etc."),
    ]


class ImportRelationshipsLogger(AsyncLogger):
    name = "importing relationships"
    steps = [
        Step("pre-import", "Disable indexes etc."),
        Step("import-table-data", "Import data into table"),
        Step("import-relationships", "Import data into table"),
        Step("post-import", "Re-enable indexes etc."),
    ]


class IndexObjectsLogger(AsyncLogger):
    name = "indexing objects"
    steps = [
        Step("delete-objects", "Delete already indexed objects for this model"),
        Step("index", "Index objects in ObjectRepository"),
    ]


class RemoveDuplicateObjectsLogger(AsyncLogger):
    name = "removing duplicate objects"
    steps = [
        Step("execute-query", "Execute N queries to remove duplicates/insert"),
    ]
