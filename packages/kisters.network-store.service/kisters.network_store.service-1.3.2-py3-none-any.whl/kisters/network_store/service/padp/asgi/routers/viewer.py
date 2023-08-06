import numpy as np
from bokeh.embed import file_html
from bokeh.models import GraphRenderer, ImageURL, MultiLine, StaticLayoutProvider
from bokeh.models.ranges import Range1d
from bokeh.models.tiles import WMTSTileSource
from bokeh.plotting import figure
from bokeh.resources import CDN
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from scipy.interpolate import make_interp_spline
from starlette import status

from kisters.network_store.service.sadp.mongodb import NetworkStore


def _centroid(a, b, loc_ref):
    va = np.array([a[loc_ref]["x"], a[loc_ref]["y"]])
    vb = np.array([b[loc_ref]["x"], b[loc_ref]["y"]])
    return np.mean(np.vstack([va, vb]), axis=0)


NODE_SIZE = 30
VERTEX_INTERPOLATION_DENSITY = 1.0 / 50.0
LINK_AS_NODE_TYPES = "Pump", "Turbine", "Valve", "Orifice"


def get_viewer_router(network_store: NetworkStore):
    viewer = APIRouter()

    @viewer.get("/{network_uid}/viewer", response_class=HTMLResponse)
    async def embedable_viewer(network_uid: str, schematic_view: bool = False):
        """Create a bokeh network viewer widget that can be embedded"""
        try:
            return await _build_embedable_viewer(network_uid, schematic_view)
        except Exception as e:
            raise HTTPException(status.HTTP_418_IM_A_TEAPOT, str(e))

    async def _build_embedable_viewer(network_uid: str, schematic_view: bool):
        fig = figure(
            x_axis_type="mercator",
            y_axis_type="mercator",
            sizing_mode="stretch_both",
        )

        # Add OpenStreetMaps background
        if schematic_view:
            loc_ref = "schematic_location"
        else:
            loc_ref = "location"
            tile_source = WMTSTileSource(
                url="http://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
                attribution=(
                    '&copy; <a href="https://www.openstreetmap.org/copyright">'
                    "OpenStreetMap</a> contributors, "
                ),
                initial_resolution=None,
            )
            fig.add_tile(tile_source)

        # Add renderer
        graph_renderer = GraphRenderer()
        fig.renderers.append(graph_renderer)

        nodes_list = await network_store.get_nodes(network_uid)
        nodes = {node["uid"]: node for node in nodes_list}
        raw_links = await network_store.get_links(network_uid)
        links = []

        for link in raw_links:
            # In hydraulic network, pumps and valves are links.
            # We display a pump (or a valve) as a link - node - link in the graph.
            if link["element_class"] in LINK_AS_NODE_TYPES:
                source_node = nodes[link["source_uid"]]
                target_node = nodes[link["target_uid"]]
                vertices = link.get("vertices", [])
                if vertices and not schematic_view:
                    # Ignore (geographic) vertices in schematic mode
                    center = vertices[len(vertices) // 2]
                else:
                    center = _centroid(source_node, target_node, loc_ref)
                nodes[link["uid"]] = {
                    "uid": link["uid"],
                    "display_name": link["display_name"],
                    loc_ref: {"x": center[0], "y": center[1]},
                    "element_class": link["element_class"],
                }
                links.append(
                    {
                        "uid": f"{source_node['uid']}__{link['uid']}",
                        "source_uid": link["source_uid"],
                        "target_uid": link["uid"],
                        "vertices": vertices[: len(vertices) // 2],
                    }
                )
                links.append(
                    {
                        "uid": f"{link['uid']}__{target_node['uid']}",
                        "source_uid": link["uid"],
                        "target_uid": link["target_uid"],
                        "vertices": vertices[len(vertices) // 2 + 1 :],
                    }
                )
            else:
                links.append(link)

        graph_renderer.node_renderer.data_source.data = {
            "index": [node["uid"] for node in nodes_list],
            "url": [f"/static/{node['element_class']}.svg" for node in nodes_list],
        }
        graph_renderer.node_renderer.glyph = ImageURL(
            # w={"value": NODE_SIZE, "units": "screen"},
            # h={"value": NODE_SIZE, "units": "screen"},
            anchor="center",
            url="url",
        )

        # Interpolate edge vertices using B-Splines
        xs = []
        ys = []
        for link in links:
            # Concatenate start coordinate, vertices, and end coordinate
            x = [
                nodes[link["source_uid"]][loc_ref]["x"],
                *(v["x"] for v in link.get("vertices", [])),
                nodes[link["target_uid"]][loc_ref]["x"],
            ]

            y = [
                nodes[link["source_uid"]][loc_ref]["y"],
                *(v["y"] for v in link.get("vertices", [])),
                nodes[link["target_uid"]][loc_ref]["y"],
            ]

            # Compute path length
            ds = np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2)
            if np.any(ds == 0):
                raise ValueError(
                    f"Please make sure that the vertices of link {link['uid']} do not"
                    " overlap with themselves or with the location of the node upstream"
                    " or downstream."
                )
            s = [np.sum(ds[0:i]) for i in range(len(x))]

            # Carry out interpolation if needed
            if len(s) > 2:
                # B-Spline order
                k = min(3, len(s) - 1)

                # If 3rd order, we want the natural B-Spline
                if k >= 3:
                    bc_type = ([(2, 0.0)], [(2, 0.0)])
                else:
                    bc_type = None

                # Fit B-Splines and interpolate for both coordinates
                spl = make_interp_spline(s, x, k=k, bc_type=bc_type)
                x = spl(
                    np.linspace(
                        0,
                        s[-1],
                        max(len(s), int(VERTEX_INTERPOLATION_DENSITY * s[-1])),
                    )
                )

                spl = make_interp_spline(s, y, k=k, bc_type=bc_type)
                y = spl(
                    np.linspace(
                        0,
                        s[-1],
                        max(len(s), int(VERTEX_INTERPOLATION_DENSITY * s[-1])),
                    )
                )

            # Store points
            xs.append(x)
            ys.append(y)

        # Add edges
        graph_renderer.edge_renderer.data_source.data = {
            "start": [link["source_uid"] for link in links],
            "end": [link["target_uid"] for link in links],
            "xs": xs,
            "ys": ys,
        }
        graph_renderer.edge_renderer.glyph = MultiLine(
            line_color="#6686ba", line_alpha=1.0, line_width=5
        )

        # Set node layout
        graph_layout = {
            node["uid"]: (node[loc_ref]["x"], node[loc_ref]["y"]) for node in nodes_list
        }
        graph_renderer.layout_provider = StaticLayoutProvider(graph_layout=graph_layout)

        # Set viewport
        x = [node[loc_ref]["x"] for node in nodes_list] + [
            v["x"] for link in links for v in link.get("vertices", [])
        ]
        y = [node[loc_ref]["y"] for node in nodes_list] + [
            v["y"] for link in links for v in link.get("vertices", [])
        ]
        min_x = np.min(x)
        max_x = np.max(x)
        min_y = np.min(y)
        max_y = np.max(y)

        margin = 0.5 * NODE_SIZE
        width = np.max([max_x - min_x, max_y - min_y]) + 2 * margin

        mean_x = np.mean([min_x, max_x])
        fig.x_range = Range1d(int(mean_x - 0.5 * width), int(mean_x + 0.5 * width))
        fig.x_range.reset_start = fig.x_range.start
        fig.x_range.reset_end = fig.x_range.end

        mean_y = np.mean([min_y, max_y])
        fig.y_range = Range1d(int(mean_y - 0.5 * width), int(mean_y + 0.5 * width))
        fig.y_range.reset_start = fig.y_range.start
        fig.y_range.reset_end = fig.y_range.end

        return file_html(fig, CDN, "network")

    return viewer
