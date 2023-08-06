import csv
from collections import defaultdict

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import InvalidEdgeIdException
from .mixins import GraphDbMixin
from .models import DatasetModel, Entity, ObjectRepository, SavedGraph
from .serializers import (
    AllNodesRelationshipsSerializer,
    ConfigSerializer,
    DetailedEdgeSerializer,
    DetailedNodeSerializer,
    NodeSerializer,
    RelationshipArgumentsSerializer,
    SavedGraphSerializer,
    UUIDListSerializer,
)


def get_first_object_or_404(ModelClass, **filters):
    """Get object (if multiple found, return first) or raise 404"""
    obj = ModelClass.objects.filter(**filters).first()
    if obj is None:
        raise Http404
    else:
        return obj


class GraphDataVisConfig(APIView):
    # TODO this endpoint should extends a base urlid_views one
    def get(self, request):
        serializer = ConfigSerializer({"entities": Entity.objects.all()})
        return Response(serializer.data)


class ExportVerticesCSVView(APIView):
    # TODO this endpoint should extends a base urlid_views one
    def build_csv(self, objs):
        all_properties, header_per_entity = [], defaultdict(list)
        for obj in objs:
            properties = obj.properties
            entity = obj.entity.name
            for key in properties.keys():
                if key not in header_per_entity[entity]:
                    header_per_entity[entity].append(key)

            properties["entity"] = entity
            properties["id"] = obj.internal_id
            all_properties.append(properties)

        header = ["entity", "id"]
        # Sort based on each entity properties
        header_per_entity = sorted(header_per_entity.items())
        for _, field_names in header_per_entity:
            header.extend(sorted(field_names))

        return header, all_properties

    def build_response(self, header, csv_data):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="vertices.csv"'
        writer = csv.DictWriter(response, fieldnames=header)
        writer.writeheader()
        writer.writerows(csv_data)
        return response

    def post(self, request, *args, **kwargs):
        ser = UUIDListSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        objs = ObjectRepository.objects.from_uuids(ser.validated_data["uuids"]).with_properties()
        header, csv_data = self.build_csv(objs)
        return self.build_response(header, csv_data)


class SavedGraphViewSet(GraphDbMixin, viewsets.ModelViewSet):
    serializer_class = SavedGraphSerializer

    def get_queryset(self):
        return SavedGraph.objects.filter(user=self.request.user).order_by("-created_at")

    def retrieve(self, request, pk=None):
        response = super().retrieve(request, pk=pk)
        edges_ids = get_object_or_404(SavedGraph, user=request.user, pk=pk).edges
        nodes, edges = self.graph.get_by_many_edges(edges_ids)
        graph_data = self.serialize_graph(nodes, edges)
        response.data["nodes"] = graph_data["nodes"]
        response.data["edges"] = graph_data["edges"]
        return response


class SavedGraphDetails(GraphDbMixin, APIView):
    def get(self, request, *args, **kwargs):
        graph_pk = kwargs.pop("pk")
        edges_ids = get_object_or_404(
            SavedGraph,
            user=request.user,
            pk=graph_pk,
        ).edges

        nodes, edges = self.graph.get_by_many_edges(edges_ids)
        return Response(self.serialize_graph(nodes, edges))


class GraphNodeDetailEndpoint(GraphDbMixin, APIView):
    serializer_class = DetailedNodeSerializer

    def get_relationships_kwargs(self, **kwargs):
        return kwargs

    def get_serializer_class(self):
        return self.serializer_class

    def get(self, request, uuid):
        # TODO: Remove coupling between uuid variable name and url definition
        # reference: https://github.com/django/django/blob/master/django/views/generic/detail.py#L16
        obj = get_first_object_or_404(ObjectRepository, uuid=uuid)
        data = self.get_serializer_class()(obj).data
        nodes, edges = self.graph.get_relationships(**self.get_relationships_kwargs(uuids=uuid))
        data["graph"] = self.serialize_graph(nodes, edges)
        return Response(data)


class NodeRelationshipsEndpoint(GraphDbMixin, APIView):
    def get_relationships_kwargs(self, **kwargs):
        ser = RelationshipArgumentsSerializer(data=self.request.GET)
        ser.is_valid(raise_exception=True)
        kwargs["depth"] = ser.validated_data["depth"]
        kwargs["inbound"] = ser.validated_data["inbound"]
        kwargs["outbound"] = ser.validated_data["outbound"]
        return kwargs

    def get(self, request, uuid):
        # TODO: Remove coupling between uuid variable name and url definition
        # reference: https://github.com/django/django/blob/master/django/views/generic/detail.py#L16
        # TODO: allow client to overwrite how to fetch for relationships directions

        obj = get_first_object_or_404(ObjectRepository, uuid=uuid)
        nodes, edges = self.graph.get_relationships(**self.get_relationships_kwargs(uuids=uuid))

        if not nodes:
            nodes = [{"uuid": obj.uuid}]

        return Response(self.serialize_graphs_per_node(nodes, edges, graph_key="graph"))


class AllNodesRelationshipsEndpoint(GraphDbMixin, APIView):
    def get_relationships_kwargs(self, **kwargs):
        ser = AllNodesRelationshipsSerializer(data=self.request.GET)
        ser.is_valid(raise_exception=True)
        uuids = ser.validated_data["uuids"]
        kwargs["uuids"] = uuids
        return kwargs

    def get(self, request):
        # TODO all endpoints calling self.graph.get_relationships shoulld implement self.get_relatinoship_kwargs method
        nodes, edges = self.graph.get_relationships(**self.get_relationships_kwargs())

        return Response(self.serialize_graphs_per_node(nodes, edges, graph_key="graph"))


class GraphEdgeDetailEndpoint(GraphDbMixin, APIView):
    serializer_class = DetailedEdgeSerializer

    def get_serializer_class(self):
        return self.serializer_class

    def get(self, request, edge_id):
        # TODO: Remove coupling between edge_id variable name and url definition
        # reference: https://github.com/django/django/blob/master/django/views/generic/detail.py#L16
        try:
            nodes, edges = self.graph.get_by_edge(edge_id)
        except InvalidEdgeIdException:
            return Response({"error": f'"{edge_id}" with invalid edge ID format'}, status=400)
        if not edges:
            raise Http404

        data = self.get_serializer_class()(instance=edges[0]).data
        data["graph"] = self.serialize_graph(nodes, edges)
        return Response(data)


class SearchOnGraphEndpoint(APIView):
    serializer_class = NodeSerializer

    def get_search_term(self):
        # TODO: Move the term logic to a proper serializer
        term = self.request.GET.get("term", "").strip()

        # Check if the term is CPF or CNPJ so we search just for the numbers.
        # Valid for:
        # - '12.345.678/9012-34'
        # - '123.456.789-01'
        # - '***.456.789-**'
        numbers = term.replace(".", "").replace("/", "").replace("-", "").replace("*", "")
        if len(numbers) in (6, 11, 14) and numbers.isdigit():
            term = numbers

        return term

    def get_serializer_class(self):
        return self.serializer_class

    def get(self, *args, **kwargs):
        term = self.get_search_term()
        if not term:
            return Response([])

        search_result = ObjectRepository.objects.search_many_entities(term)
        unique_result = []
        added_uuids = set()
        for item in search_result:
            if item.uuid not in added_uuids:
                unique_result.append(item)
                added_uuids.add(item.uuid)
        return Response(self.get_serializer_class()(unique_result, many=True).data)


class ShortestPathEndpoint(GraphDbMixin, APIView):
    def get(self, request, from_uuid, to_uuid, *args, **kwargs):
        nodes, edges = self.graph.get_shortest_path(from_uuid, to_uuid)
        return Response(self.serialize_graph(nodes, edges))


class DatasetFilter(APIView):
    def get_model(self, slug):
        dataset_models = DatasetModel.subclasses()
        if slug not in dataset_models:
            raise Http404
        return dataset_models[slug]

    def get(self, request, slug, object_uuid):
        Model = self.get_model(slug)
        if hasattr(Model.objects, "for_object"):
            objects = Model.objects.for_object(object_uuid=object_uuid)
        else:
            objects = Model.objects.filter(object_uuid=object_uuid)
        data = {
            "fields": Model.fields(),
            "result": [obj.serialize() for obj in objects],
        }
        data.update(Model.extra(objects))
        return Response(data)
