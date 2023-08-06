from cached_property import cached_property

from .graph_db import get_relationships_graph
from .models import ObjectRepository
from .serializers import DetailedEdgeSerializer, DetailedNodeSerializer


class GraphDbMixin:
    node_serializer_class = DetailedNodeSerializer
    edge_serializer_class = DetailedEdgeSerializer

    @cached_property
    def graph(self):
        return get_relationships_graph()

    def serialize_graph(self, nodes, edges):
        """
        nodes and edges as returned by RelationshipsGraph query methods
        """
        nodes_objs = ObjectRepository.objects.from_uuids([n["uuid"] for n in nodes]).with_properties()
        return self.serialize_graph_objects(nodes_objs, edges)

    def serialize_graph_objects(self, nodes_objs, edges):
        """
        nodes_objs are Object and edges are edges returned by RelationshipsGraph
        """
        return {"nodes": self.serialize_nodes(nodes_objs), "edges": self.serialize_edges(edges)}

    def serialize_graphs_per_node(self, nodes, edges, graph_key, serializer_class=None):
        data = {}

        nodes_objs = ObjectRepository.objects.from_uuids([n["uuid"] for n in nodes]).with_properties()
        for node in nodes_objs:
            node_uuid = str(node.uuid)
            graph_edges = [e for e in edges if node_uuid in (e["to"], e["from"])]
            graph_nodes = set()
            for edge in graph_edges:
                from_node = [n for n in nodes_objs if str(n.uuid) == edge["from"]]
                to_node = [n for n in nodes_objs if str(n.uuid) == edge["to"]]
                if from_node:
                    graph_nodes.add(from_node[0])
                if to_node:
                    graph_nodes.add(to_node[0])

            serializer_class = serializer_class or self.get_node_serializer_class()
            node_data = serializer_class(node).data
            node_data[graph_key] = self.serialize_graph_objects(graph_nodes, graph_edges)
            data[node_uuid] = node_data

        return data

    def serialize_nodes(self, nodes_objs):
        Serializer = self.get_node_serializer_class()
        return Serializer(nodes_objs, many=True).data

    def serialize_edges(self, edges_objs):
        Serializer = self.get_edge_serializer_class()
        return Serializer(edges_objs, many=True).data

    def get_node_serializer_class(self):
        return self.node_serializer_class

    def get_edge_serializer_class(self):
        return self.edge_serializer_class

    def get_relationships_kwargs(self, **kwargs):
        raise NotImplementedError
