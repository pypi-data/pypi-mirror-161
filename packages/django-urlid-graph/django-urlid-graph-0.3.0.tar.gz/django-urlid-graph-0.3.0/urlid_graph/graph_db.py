from collections import namedtuple

from django.db import connections

import urlid_graph.settings as urlid_graph_settings

from .exceptions import (
    InvalidEdgeIdException,
    InvalidRelationshipsDirectionsException,
    UnexpectedCypherQueryTypeException,
)

EDGE_ID_SEPARATOR_TOKEN = "|"

EdgeInfo = namedtuple("EdgeInfo", ["label", "from_uuid", "to_uuid"])


class RelationshipsGraph:
    @property
    def db_connection(self):
        return connections[urlid_graph_settings.GRAPH_DATABASE]

    def _fetch_path(self, cursor, path_query, args={}):
        uuids_by_node_ids = {}
        cursor.execute(path_query, args)

        nodes, edges = [], {}
        for data in cursor.fetchall():
            for path_data in data:
                p_type = path_data["type"]
                if p_type != "path":
                    error_msg = f"Query must be fetching for path, not {p_type}"
                    raise UnexpectedCypherQueryTypeException(error_msg)

                for v in path_data["vertices"]:
                    uuids_by_node_ids[v["vid"]] = v["uuid"]
                    nodes.append({"uuid": v["uuid"]})

                for e in path_data["edges"]:
                    from_ = uuids_by_node_ids[e.pop("source_vid")]
                    to = uuids_by_node_ids[e.pop("destination_vid")]
                    label = e.pop("label")

                    edge_info = EdgeInfo(label, from_, to)
                    id_ = create_edge_id(edge_info)

                    edges[id_] = {
                        "from": from_,
                        "to": to,
                        "label": label,
                        "id": id_,
                        "properties": e.get("properties", {}),
                    }

        return nodes, list(edges.values())

    def get_relationships(self, uuids, depth=0, inbound=True, outbound=True):
        if not isinstance(uuids, tuple):
            uuids = (str(uuids),)

        s_dir, t_dir = "-", "-"
        if inbound and not outbound:
            s_dir = "<-"
        elif outbound and not inbound:
            t_dir = "->"
        elif not inbound and not outbound:
            raise InvalidRelationshipsDirectionsException("Parameters inbound and outbound can not be both False")

        uuids_placeholders = ", ".join("%s" for _ in uuids)
        query = (
            "MATCH path=(n)<S_DIR>[*0..%s]<T_DIR>() WHERE n.uuid IN [<UUIDS>] RETURN path".replace(
                "<UUIDS>", uuids_placeholders
            )
            .replace("<S_DIR>", s_dir)
            .replace("<T_DIR>", t_dir)
        )
        nodes, edges = [], []
        query_args = (depth + 1, *uuids)
        with self.db_connection.cursor() as cursor:
            q_nodes, q_edges = self._fetch_path(cursor, query, query_args)
            nodes.extend(q_nodes)
            edges.extend(q_edges)

        return nodes, edges

    def get_by_edge(self, edge_id):
        edge_info = parse_edge_id(edge_id)

        query = (
            "MATCH path=({uuid:'<VFROM>'})-[:<ELABEL>]->({uuid:'<VTO>'}) RETURN path".replace(
                "<VFROM>", edge_info.from_uuid
            )
            .replace("<VTO>", edge_info.to_uuid)
            .replace("<ELABEL>", edge_info.label)
        )

        with self.db_connection.cursor() as cursor:
            return self._fetch_path(cursor, query)

    def get_by_many_edges(self, edges_ids):
        from_uuids, to_uuids = [], []
        for edge_id in edges_ids:
            edge_info = parse_edge_id(edge_id)
            from_uuids.append(edge_info.from_uuid)
            to_uuids.append(edge_info.to_uuid)

        query = (
            "MATCH path=(o1:object)-[]-(o2:object)"
            " WHERE o1.uuid IN {from_uuids} AND o2.uuid IN {to_uuids} RETURN path;"
        ).format(from_uuids=from_uuids, to_uuids=to_uuids)

        with self.db_connection.cursor() as cursor:
            return self._fetch_path(cursor, query)

    def get_shortest_path(self, from_uuid, to_uuid, limit=20):
        # There is also allShortestPaths
        query = (
            "MATCH (o1: object), (o2: object),"
            f" path=shortestpath((o1)-[*..{limit}]-(o2))"
            f" WHERE o1.uuid = '{from_uuid}' AND o2.uuid = '{to_uuid}'"
            " RETURN path;"
        )
        with self.db_connection.cursor() as cursor:
            return self._fetch_path(cursor, query)


def parse_edge_id(value):
    data = value.split(EDGE_ID_SEPARATOR_TOKEN)
    if len(data) != 3 or not data[0]:
        raise InvalidEdgeIdException(f"Value {repr(value)} not in format 'label|from_uuid|to_uuid'")

    return EdgeInfo(*data)


def create_edge_id(edge_info):
    return EDGE_ID_SEPARATOR_TOKEN.join(edge_info)


def get_relationships_graph():
    return RelationshipsGraph()
