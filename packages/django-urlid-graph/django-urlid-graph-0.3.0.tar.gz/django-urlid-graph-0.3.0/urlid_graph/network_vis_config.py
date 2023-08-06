from urlid_graph import settings as urlid_graph_settings

EXPANDED_SUFFIX = "_expanded"


graph_vis_options = {
    "all_nodes_relationships_chunk_size": urlid_graph_settings.ALL_NODES_RELATIONSHIPS_CHUNK_SIZE,
    "expanded_node_group_suffix": EXPANDED_SUFFIX,
    "edges": {
        "arrows": {"to": {"enabled": True}},
        "color": {"color": "#ed8936", "highlight": "#ed8936"},
        "font": {"color": "#1a202c", "align": "top"},
    },
    "nodes": {
        "font": {"color": "#1a202c", "strokeWidth": 2, "strokeColor": "#ffffff"},
    },
    "physics": {
        "enabled": True,
        "barnesHut": {"gravitationalConstant": -50000, "springConstant": 0.01},
        "stabilization": {"enabled": True, "iterations": 2000, "updateInterval": 10},
    },
    "groups": {},
}


def get_entity_node_config(entity):
    node_cfg = entity.graph_node_conf or {}
    background_color_collapsed = node_cfg.get("background-collapsed", "#61b2fe")
    background_color_expanded = node_cfg.get("background-expanded", "#3182ce")
    color_collapsed = node_cfg.get("color-collapsed", "#fff")
    color_expanded = node_cfg.get("color-expanded", "#fff")
    icon = icon_expanded = node_cfg.get("code", "")

    return {
        entity.name: {
            "color": {
                "border": background_color_collapsed,
                "background": background_color_collapsed,
                "highlight": {
                    "border": "white",
                    "background": background_color_collapsed,
                },
            },
            "shape": "dot",
            "icon": {
                "code": icon,
                "color": color_collapsed,
                "description": f"{entity.label} sem relações expandidas",
                "face": '"Font Awesome 5 Free"',
                "size": 50,
            },
        },
        f"{entity.name}{EXPANDED_SUFFIX}": {
            "shadow": {"enabled": True, "size": "8"},
            "color": {
                "border": background_color_expanded,
                "background": background_color_expanded,
                "highlight": {
                    "border": "white",
                    "background": background_color_expanded,
                },
            },
            "shape": "dot",
            "icon": {
                "code": icon_expanded,
                "color": color_expanded,
                "description": f"{entity.label} com todas as relações já expandidas",
                "face": '"Font Awesome 5 Free"',
                "size": 50,
            },
        },
    }
