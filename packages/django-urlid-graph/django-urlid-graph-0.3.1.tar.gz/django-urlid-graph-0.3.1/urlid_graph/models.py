import datetime
import re
import uuid
from collections import defaultdict
from functools import lru_cache
from textwrap import dedent
from urllib.parse import urljoin

import django.db.models.options as options
from cached_property import cached_property
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVectorField
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections, models
from django.template import Context, Template

from urlid_graph import settings as urlid_graph_settings
from urlid_graph.utils import random_name

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("entity_name", "entity_uuid", "search_fields", "slug")


REGEXP_CAMEL_CASE = re.compile("([A-Z])")


def get_urlid_database_uri():
    db = settings.DATABASES[urlid_graph_settings.DJANGO_DATABASE]
    return f"postgres://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}"


def slug_from_model_name(name):
    """
    >>> slug_from_model_name('SomeDataset')
    'some-dataset'
    >>> slug_from_model_name('MyTestModel')
    'my-test'
    """

    name = REGEXP_CAMEL_CASE.sub(r"-\1", name).lower()
    if name[0] == "-":
        name = name[1:]
    if name[-1] == "-":
        name = name[:-1]
    if name.endswith("-model"):
        name = name[:-6]
    return name


@lru_cache(maxsize=64)
def get_template(template_code):
    return Template(template_code)


class EntityQuerySet(models.QuerySet):
    def by_name(self, names):
        return self.filter(name__in=[name.lower().strip() for name in names])


class Entity(models.Model):
    objects = EntityQuerySet.as_manager()

    uuid = models.UUIDField(primary_key=True)
    base_url = models.TextField(blank=False, null=False)
    name = models.TextField(blank=False, null=False)
    version = models.TextField(blank=False, null=False)

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"

    @property
    def url(self):
        return urljoin(self.base_url, f"/{self.name}/v{self.version}/")

    @property
    def label_properties(self):
        return getattr(self.config, "label_properties", None) or []

    @property
    def label_template(self):
        return getattr(self.config, "label_template", None) or None

    @property
    def graph_node_conf(self):
        return getattr(self.config, "graph_node_conf", None) or {}

    @property
    def config(self):
        try:
            return EntityConfig.objects.for_entity(self.name)
        except ObjectDoesNotExist:
            return None

    @property
    def label(self):
        return getattr(self.config, "label", None) or self.name

    def __str__(self):
        return f"Entity {self.url}"

    def get_model(self):
        for Model in ObjectModelMixin.__subclasses__():
            if str(Model._meta.entity_uuid) == str(self.uuid):
                return Model


class ObjectMixin:
    """Mixin used by Object and ObjectRepository classes"""

    @property
    def url(self):
        # TODO: change
        return urljoin(self.entity.url, f"{self.uuid}/")

    def _get_objects(self):
        ObjectModel = self.entity.get_model()
        if ObjectModel is None:
            raise ValueError("Model class not found fo entity UUID {}".format(self.entity.uuid))

        return ObjectModel.objects.filter(object_uuid=self.uuid).order_by(models.F("updated_at").asc(nulls_first=True))

    @cached_property
    def properties(self):
        data = {}
        for obj in self._get_objects():
            data.update(obj.serialize())
        return data

    @cached_property
    def raw_properties(self):
        data = {}
        for obj in self._get_objects():
            data.update(obj.raw_serialize())
        return data

    @cached_property
    def full_properties(self):
        data = defaultdict(list)
        for obj in self._get_objects():
            for key, value in obj.serialize():
                data[key].append(
                    {
                        "value": value,
                        "value_type": 1,  # TODO: change?
                        "source": "?",  # TODO: change?
                        "value_datetime": obj.updated_at.isoformat() if obj.updated_at else None,
                    }
                )
        return data

    @property
    def label(self):
        label_template = self.entity.label_template
        props = self.raw_properties
        if label_template is not None:
            return get_template(label_template).render(Context(props))
        else:
            for prop_name in self.entity.label_properties:
                label = props.get(prop_name)
                if label:
                    return label
        return f"{self.entity.name}: {self.uuid}"

    def get_label_for_property(self, prop_name):
        try:
            config = EntityPropertyConfig.objects.for_object(self.entity.name, prop_name)
            return config.label
        except ObjectDoesNotExist:
            return prop_name

    def __str__(self):
        return f"Object {self.uuid}"


class PropertyQuerySet(models.QuerySet):
    def for_object(self, obj):
        return self.filter(object_id=obj.uuid)

    def for_objects(self, objs):
        return self.filter(object_id__in=[obj.uuid for obj in objs])


class EntityConfigManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(config_type=ElementConfig.ENTITY_CONFIG)

    @lru_cache()
    def for_entity(self, entity_name):
        return self.get_queryset().get(name=entity_name)


class RelationshipConfigManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(config_type=ElementConfig.REL_CONFIG)

    @lru_cache()
    def get_by_name(self, relationship_name):
        return self.get_queryset().get(name=relationship_name)


class EntityPropertyConfigManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(config_type=ElementConfig.PROPERTY_CONFIG, parent_type=ElementConfig.ENTITY_CONFIG)

    @lru_cache()
    def for_object(self, parent_name, prop_name):
        return self.get_queryset().get(parent_name=parent_name, name=prop_name)


class RelPropertyConfigManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(config_type=ElementConfig.PROPERTY_CONFIG, parent_type=ElementConfig.REL_CONFIG)


class StatsConfigManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(config_type=ElementConfig.STATS_CONFIG)

    def get_stats(self):
        return self.get(name="stats")


class ElementConfig(models.Model):
    ENTITY_CONFIG, REL_CONFIG, PROPERTY_CONFIG, STATS_CONFIG = 1, 2, 3, 4
    TYPE_CHOICES = [
        (ENTITY_CONFIG, "entity"),
        (REL_CONFIG, "relationship"),
        (PROPERTY_CONFIG, "property"),
        (STATS_CONFIG, "stats"),
    ]
    PARENT_TYPE_CHOICES = [
        (ENTITY_CONFIG, "entity"),
        (REL_CONFIG, "relationship"),
    ]

    config_type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    name = models.TextField()
    parent_type = models.PositiveSmallIntegerField(choices=PARENT_TYPE_CHOICES, null=True)
    parent_name = models.TextField(null=True)
    label = models.TextField()
    data = models.JSONField()

    class Meta:
        unique_together = ["config_type", "name", "parent_type", "parent_name"]
        verbose_name = "Element configuration"
        verbose_name_plural = "Element configurations"


class EntityConfig(ElementConfig):
    objects = EntityConfigManager()

    class Meta:
        proxy = True

    @property
    def label_properties(self):
        return self.data.get("label_properties", [])

    @property
    def label_template(self):
        return self.data.get("label_template", None)

    @property
    def graph_node_conf(self):
        return self.data.get("graph_node_conf", {})


class RelationshipConfig(ElementConfig):
    objects = RelationshipConfigManager()

    class Meta:
        proxy = True

    @property
    def from_graph_node_conf(self):
        return self.data.get("from_graph_node_conf", {})

    @property
    def to_graph_node_conf(self):
        return self.data.get("to_graph_node_conf", {})


class EntityPropertyConfig(ElementConfig):
    objects = EntityPropertyConfigManager()

    class Meta:
        proxy = True


class RelPropertyConfig(ElementConfig):
    objects = RelPropertyConfigManager()

    class Meta:
        proxy = True


class StatsConfig(ElementConfig):
    objects = StatsConfigManager()

    class Meta:
        proxy = True


class ObjectRepositoryQuerySet(models.QuerySet):
    def from_uuids(self, uuids):
        return self.filter(uuid__in=uuids).select_related("entity")

    def with_properties(self):
        # TODO: is this still needed?
        qs = []
        for obj in self.all():
            obj.__dict__["properties"] = obj.properties
            qs.append(obj)
        return qs

    def index(self, Model, start_id=None, lang="pg_catalog.portuguese", batch_size=10000, callback=None):
        """Update the FTS index using objects from `Model`"""

        table_name = Model._meta.db_table
        temp_table_name = "urlid_tmp_fts_" + random_name(16)
        create_temp_table_sqls = [
            (
                f'CREATE TEMPORARY TABLE "{temp_table_name}" ("id" SERIAL, "uuid" UUID)',
                [],
            ),
            (
                dedent(
                    f"""
                    INSERT INTO "{temp_table_name}" ("uuid")
                    SELECT DISTINCT object_uuid FROM "{table_name}" WHERE id >= %s
                    """
                ).strip(),
                [start_id or 0],
            ),
            (
                f'CREATE INDEX "idx_{random_name(20)}" ON "{temp_table_name}" ("id", "uuid")',
                [],
            ),
        ]
        row_count = []
        with connections[urlid_graph_settings.DJANGO_DATABASE].cursor() as cursor:
            for sql, args in create_temp_table_sqls:
                cursor.execute(sql, args)
                row_count.append(cursor.rowcount)
        total_objects = row_count[1]

        string_agg = " || ' ' || ".join(
            f"COALESCE(STRING_AGG({field_name}, ' '), '')" for field_name in Model._meta.search_fields
        )
        insert_sql = dedent(
            f"""
            INSERT INTO "{ObjectRepository._meta.db_table}" (uuid, entity_id, search_data)
                SELECT
                    object_uuid,
                    %s::uuid,
                    to_tsvector(
                        %s,
                        {string_agg}
                    )
                FROM "{table_name}"
                WHERE object_uuid IN (
                    SELECT "uuid"
                    FROM "{temp_table_name}"
                    WHERE id >= %s AND id < %s
                )
                GROUP BY object_uuid
            ON CONFLICT (uuid) DO UPDATE SET search_data = EXCLUDED.search_data
            """
        ).strip()

        counter = 0
        for object_id in range(1, total_objects + 1, batch_size):
            args = (Model._meta.entity_uuid, lang, object_id, object_id + batch_size)
            with connections[urlid_graph_settings.DJANGO_DATABASE].cursor() as cursor:
                cursor.execute(insert_sql, args)
                counter += cursor.rowcount
                if callback is not None:
                    callback(done=counter, total=total_objects)

        drop_temp_table_sql = f'DROP TABLE "{temp_table_name}"'
        with connections[urlid_graph_settings.DJANGO_DATABASE].cursor() as cursor:
            cursor.execute(drop_temp_table_sql)

        return counter

    def search(self, search_query, config=urlid_graph_settings.SEARCH_LANGUAGE):
        """Full-Text Search in object's search_data"""

        qs = self.filter()
        search_query = search_query or ""
        if not search_query:
            return qs
        words = search_query.split()
        query = None
        done = []  # to preserve order
        for word in words:
            if not word or word in done:
                continue
            if query is None:
                query = SearchQuery(word, config=config)
            else:
                query = query & SearchQuery(word, config=config)
            done.append(word)
        qs = qs.annotate(search_rank=SearchRank(models.F("search_data"), query)).filter(search_data=query)
        # Using `qs.query.add_ordering` will APPEND ordering fields instead
        # of OVERWRITTING (`qs.order_by` will overwrite).
        qs.query.add_ordering("-search_rank")
        return qs

    def search_many_entities(self, query, entities=all, limit_per_entity=10):
        """Search objects in more than one entity, by name

        Prefer to use this method since it also filter objects by entity (more performance)"""

        if entities is all:
            entities = Entity.objects.all()
        else:
            entities = Entity.objects.by_name(entities)

        results = []
        for entity in entities:
            qs = self.filter(entity=entity).search(query).select_related("entity")
            results.extend(qs[:limit_per_entity])
        results.sort(key=lambda row: row.search_rank, reverse=True)
        return results


class ObjectRepository(ObjectMixin, models.Model):
    objects = ObjectRepositoryQuerySet.as_manager()

    uuid = models.UUIDField(primary_key=True)
    entity = models.ForeignKey(Entity, on_delete=models.DO_NOTHING, db_constraint=False, db_index=False)
    search_data = SearchVectorField(null=True)

    class Meta:
        indexes = [GinIndex(fields=["search_data"])]
        verbose_name = "Object repository"
        verbose_name_plural = "Object repositories"


class SavedGraph(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    edges = ArrayField(models.CharField(max_length=255))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        unique_together = (("user", "name"),)
        verbose_name = "Saved graph"
        verbose_name_plural = "Saved graphs"


class ObjectModelMixin(models.Model):
    object_uuid = models.UUIDField(null=False, blank=False, db_index=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def raw_serialize(self):
        return {field.name: getattr(self, field.name) for field in self._meta.fields if field.name != "search_data"}

    class Meta:
        abstract = True


class DatasetModel(models.Model):
    object_uuid = models.UUIDField(
        verbose_name="Object UUID",
        help_text="UUID of described object",
        null=False,
        blank=False,
        db_index=True,
    )

    @classmethod
    def extra(cls, qs):
        return {}

    @classmethod
    def fields(cls):
        from django.db import connection

        return [
            {
                "name": field.name,
                "title": field.verbose_name,
                "type": field.db_type(connection),
                "description": field.help_text,
            }
            for field in cls._meta.fields
            if field.name not in ("id", "object_uuid")
        ]

    @cached_property
    def serializers(self):
        return {
            attribute[len("serialize_") :]: getattr(self, attribute)
            for attribute in dir(self)
            if attribute.startswith("serialize_")
        }

    def serialize(self):
        row = []
        for field in type(self).fields():
            field_name = field["name"]
            value = getattr(self, field["name"])
            if field_name in self.serializers:
                value = self.serializers[field_name](value)
            row.append(value)
        return row

    @classmethod
    def subclasses(cls):
        data = {}
        for klass in cls.__subclasses__():
            if hasattr(klass._meta, "slug"):
                slug = klass._meta.slug
            else:
                slug = slug_from_model_name(klass.__name__)
            data[slug] = klass
        return data

    class Meta:
        abstract = True


class JobLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def current_step(self):
        return self.steps.first().step

    @property
    def progress(self):
        step = self.steps.first()
        if step.done is not None and step.total is not None and step.total != 0:
            return f"{100 * step.done / step.total:5.2f}%"
        else:
            result = step.step + (f" ({step.action})" if step.action else "")
            if self.steps.filter(action="error").count() > 0:
                result += " - has error"
            return result

    @property
    def eta(self):
        step = self.steps.first()
        if step.done is None or step.total is None or step.total == 0:
            return "-"
        first_step = self.steps.exclude(pk=step.pk).filter(step=step.step, done__gt=0).order_by("created_at").first()
        if first_step is None:
            return "-"
        to_finish = step.total - step.done
        delta_done = step.done - first_step.done
        delta_time = (step.created_at - first_step.created_at).total_seconds()
        speed = delta_done / delta_time
        result = str(datetime.timedelta(seconds=to_finish / speed))
        return result.split(".")[0]

    @property
    def last_updated_at(self):
        return self.steps.first().created_at

    def __str__(self):
        return f"{self.name} - {self.description}: {self.id}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            super().save(*args, **kwargs)
            LogStep.objects.create(job=self, action="started", step="created")
        else:
            super().save(*args, **kwargs)


class LogStep(models.Model):
    job = models.ForeignKey(JobLog, related_name="steps", on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    step = models.CharField(max_length=255)
    done = models.FloatField(null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.step} - {self.action}: {self.job.id}"
