from collections import OrderedDict
from copy import deepcopy

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from urlid_graph import settings as urlid_graph_settings

from .exceptions import InvalidEdgeIdException
from .formatting import format_property_value, format_unknown_property_value
from .graph_db import parse_edge_id
from .models import ObjectRepository, RelationshipConfig, RelPropertyConfig, SavedGraph


def _sorted_properties(props):
    return OrderedDict([(k, v) for k, v in sorted(props.items(), key=lambda p: p[0])])


class ConfigSerializer(serializers.Serializer):
    options = serializers.SerializerMethodField()
    endpoints = serializers.SerializerMethodField()

    def get_options(self, obj):
        from urlid_graph.network_vis_config import get_entity_node_config, graph_vis_options

        options = deepcopy(graph_vis_options)

        for entity in obj["entities"]:
            options["groups"].update(get_entity_node_config(entity))

        return options

    def get_endpoints(self, obj):
        return {"search": reverse("graph_api:search")}


class UUIDListSerializer(serializers.Serializer):
    uuids = serializers.ListField(child=serializers.UUIDField())

    def validate_uuids(self, value):
        if len(value) > urlid_graph_settings.NODES_CSV_SIZE_LIMIT:
            raise serializers.ValidationError(
                f"Number of nodes exceeded maximum {urlid_graph_settings.NODES_CSV_SIZE_LIMIT}"
            )
        return value


class EdgeIdField(serializers.Field):
    edge_id = serializers.CharField()

    def to_representation(self, value):
        return value

    def to_internal_value(self, value):
        try:
            edge_info = parse_edge_id(value)
        except InvalidEdgeIdException:
            raise serializers.ValidationError("Edge(s) not in correct format: 'label|from_id|to_id'")
        serializers.UUIDField().to_internal_value(edge_info.from_uuid)
        serializers.UUIDField().to_internal_value(edge_info.to_uuid)

        return value


class SavedGraphSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    edges = serializers.ListField(child=EdgeIdField())
    name = serializers.CharField()
    created_at = serializers.DateTimeField(
        required=False,
        format="%d/%m/%Y %H:%M",
        read_only=True,
    )

    def to_representation(self, obj):
        response = super().to_representation(obj)
        if self.context["request"].method == "GET":
            response.pop("edges")

        return response

    def get_name(self, value):
        return value.strip()

    def create(self, validated_data):
        return SavedGraph.objects.create(**validated_data)

    class Meta:
        model = SavedGraph
        fields = ["pk", "user", "name", "edges", "created_at"]
        validators = [UniqueTogetherValidator(queryset=SavedGraph.objects.all(), fields=["user", "name"])]


class EdgeSerializer(serializers.Serializer):
    name = serializers.CharField(source="label")
    to = serializers.CharField()
    id = serializers.CharField()
    label = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        # from is a reserved word and can't be used to declare fields the same
        # way as the others are declared
        self.fields["from"] = serializers.CharField()
        super().__init__(*args, **kwargs)

    def get_label(self, obj):
        edge_label = obj["label"]
        try:
            return RelationshipConfig.objects.get_by_name(edge_label).label
        except ObjectDoesNotExist:
            return edge_label


class DetailedEdgeSerializer(EdgeSerializer):
    properties = serializers.SerializerMethodField()

    def get_properties(self, obj):
        props = {}
        edge_label = obj["label"]
        for name, value in obj["properties"].items():
            try:
                key = RelPropertyConfig.objects.get(parent_name=edge_label, name=name).label
            except ObjectDoesNotExist:
                key = name
            props[key] = format_unknown_property_value(name, key, value)
        return _sorted_properties(props)


class NodeSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source="entity.name")
    label = serializers.CharField()
    id = serializers.CharField(source="uuid")

    class Meta:
        model = ObjectRepository
        fields = ["id", "group", "label"]

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["properties"] = instance.properties
        return result


class DetailedNodeSerializer(NodeSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = NodeSerializer.Meta.model
        fields = NodeSerializer.Meta.fields + ["properties"]

    def get_properties(self, obj):
        props = {}
        for name, value in obj.properties.items():
            key = obj.get_label_for_property(name)
            props[key] = format_property_value(name, key, value)
        return _sorted_properties(props)


class FullPropertiesNodeSerializer(DetailedNodeSerializer):
    full_properties = serializers.SerializerMethodField()

    class Meta:
        model = DetailedNodeSerializer.Meta.model
        fields = DetailedNodeSerializer.Meta.fields + ["full_properties"]

    def get_full_properties(self, obj):
        props = {}
        for name, value in obj.full_properties.items():
            key = obj.get_label_for_property(name)
            props[key] = []
            for prop_value in value:
                prop_value["value"] = format_property_value(name, key, prop_value["value"])
                props[key].append(prop_value)
        return props


class RelationshipArgumentsSerializer(serializers.Serializer):
    depth = serializers.IntegerField(default=0, min_value=0, max_value=urlid_graph_settings.RELATIONSHIP_DEPTH_LIMIT)
    inbound = serializers.BooleanField(default=True)
    outbound = serializers.BooleanField(default=True)

    def validate(self, attrs):
        if attrs["inbound"] is False and attrs["outbound"] is False:
            raise serializers.ValidationError("Parameters inbound and outbound can not be both False")

        return attrs


class AllNodesRelationshipsSerializer(serializers.Serializer):
    uuids = serializers.ListField(
        child=serializers.UUIDField(), max_length=urlid_graph_settings.ALL_NODES_RELATIONSHIPS_CHUNK_SIZE, min_length=1
    )

    def validate(sel, attrs):
        return {"uuids": tuple(str(u) for u in attrs["uuids"])}
