from django.urls import path, re_path

from . import views

list_actions = {"get": "list", "post": "create"}
single_actions = {
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
}


app_name = "graph_api"

urlpatterns = [
    path("config", views.GraphDataVisConfig.as_view(), name="config"),
    path(
        "dataset/<str:slug>/<uuid:object_uuid>",
        views.DatasetFilter.as_view(),
        name="dataset-filter",
    ),
    path(
        "edge/<str:edge_id>",
        views.GraphEdgeDetailEndpoint.as_view(),
        name="edge_detail",
    ),
    path(
        "export-properties-csv",
        views.ExportVerticesCSVView.as_view(),
        name="export-properties-csv",
    ),
    path(
        "node/<uuid:uuid>",
        views.GraphNodeDetailEndpoint.as_view(),
        name="node_detail",
    ),
    path(
        "node/<uuid:uuid>/relationships",
        views.NodeRelationshipsEndpoint.as_view(),
        name="node_rels",
    ),
    path(
        "node/relationships",
        views.AllNodesRelationshipsEndpoint.as_view(),
        name="all_nodes_rels",
    ),
    path(
        "save-graph",
        views.SavedGraphViewSet.as_view(list_actions),
        name="save-graph",
    ),
    re_path(
        "^save-graph/(?P<pk>\d*)$",
        views.SavedGraphViewSet.as_view(single_actions),
        name="save-graph",
    ),  # noqa
    re_path(
        "^saved-graph-detail/(?P<pk>\d*)$",
        views.SavedGraphDetails.as_view(),
        name="saved-graph-detail",
    ),  # noqa
    path("search", views.SearchOnGraphEndpoint.as_view(), name="search"),
    path(
        "shortest-path/<uuid:from_uuid>/<uuid:to_uuid>",
        views.ShortestPathEndpoint.as_view(),
        name="shortest_path",
    ),
]
