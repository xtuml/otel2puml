"""A Dash app for visualising OpenTelemetry data"""
from dash import Dash, html, dcc, Output, Input, callback, State
import dash.exceptions
import os
import sys
import base64
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from typing import Generator, Any

import networkx as nx

from tel2puml.pv_to_puml import (
    pv_jobs_from_folder_to_puml_file,
    pv_jobs_from_folder_to_event_sequence_streams,
)
from tel2puml.data_pipelines.data_ingestion import (
    get_graph_solutions_from_clustered_events,
)

image_filename = "proof_of_concepts/dash_app/assets/simple.svg"

encoded_image = base64.b64encode(open(image_filename, "rb").read()).decode()


input_data_folder_path = "."

app = Dash(
    __name__, external_stylesheets=[dbc.themes.CYBORG, "/assets/custom.css"]
)

folder_names_and_paths = {}
cyto_graph_elements: list[list[dict]] = []

args = sys.argv[1:]
if len(args) < 2:
    print(
        "Usage: python app.py <path_to_folder_of_jobs> <path_to_plantuml_jar>"
    )
    sys.exit(1)
input_data_folder_path = args[0]
plantuml_jar_path = args[1]
for folder_name in os.listdir(input_data_folder_path):
    folder_path = os.path.join(input_data_folder_path, folder_name)
    if os.path.isdir(folder_path):
        folder_names_and_paths[folder_name] = folder_path


# the style arguments for the sidebar
SIDEBAR_STYLE = {
    "padding": "2rem 1rem",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.

cyto_content = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(
                                            "Options",
                                            className=(
                                                "text-center "
                                                "bg-body-tertiary "
                                                "text-body-tertiary"
                                            ),
                                        )
                                    ],
                                    style={
                                        "width": "100%",
                                        "height": "100%",
                                        "padding": "5px",
                                    },
                                    className="bg-body-tertiary card",
                                )
                            ],
                            style={
                                "width": "35%",
                                "height": "100%",
                                "display": "flex",
                                "flexDirection": "column",
                                "padding-right": "5px",
                                "padding-left": "0px",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(
                                            "Run from folder",
                                            className=(
                                                "text-center "
                                                "bg-body-tertiary "
                                                "text-body-tertiary"
                                            ),
                                            style={
                                                "width": "100%",
                                                "height": "30%",
                                            },
                                        ),
                                        html.Div(
                                            children=[
                                                dcc.Dropdown(
                                                    list(
                                                        folder_names_and_paths.
                                                        keys()
                                                    ),
                                                    id="pandas-dropdown-2",
                                                    placeholder="Select folder"
                                                    " of jobs",
                                                ),
                                                html.Button(
                                                    "Run",
                                                    id="run-button",
                                                    n_clicks=0,
                                                    className="btn "
                                                    "btn-primary",
                                                    style={
                                                        "maxwidth": "80px",
                                                        "width": "20%",
                                                    },
                                                ),
                                            ],
                                            id="my-dropdown-parent",
                                            style={
                                                "display": "flex",
                                                "flexDirection": "row",
                                                "width": "100%",
                                                "height": "50%",
                                                "max-height": "35px",
                                            },
                                            className="input-group",
                                        ),
                                    ],
                                    style={
                                        "width": "100%",
                                        "height": "100%",
                                        "padding": "5px",
                                    },
                                    className="bg-body-tertiary card",
                                )
                            ],
                            style={
                                "width": "65%",
                                "height": "100%",
                                "display": "flex",
                                "flexDirection": "column",
                                "padding-left": "0px",
                                "padding-right": "0px",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "row",
                        "width": "100%",
                        "height": "25%",
                        "padding-bottom": "5px",
                    },
                ),
                html.Div(
                    [
                        html.H3(
                            "Unique Graph Viewer",
                            className="text-center "
                            "bg-body-tertiary text-body-tertiary",
                            style={
                                "width": "100%",
                                "height": "10%",
                                "padding": "5px",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            list(
                                                range(len(cyto_graph_elements))
                                            ),
                                            id="drop_down_for_graphs",
                                            placeholder="Select unique graph",
                                            style={
                                                "height": "100%",
                                            },
                                            className="drop_down_uniq_graph "
                                            "border border-light",
                                        ),
                                        html.Button(
                                            "Reset Axes",
                                            id="reset-axes",
                                            n_clicks=0,
                                            className="btn btn-primary",
                                            style={
                                                "width": "20%",
                                                "height": "100%",
                                                "min-width": "120px",
                                            },
                                        ),
                                    ],
                                    style={
                                        "width": "100%",
                                        "height": "10%",
                                        "max-height": "35px",
                                        "display": "flex",
                                        "flexDirection": "row",
                                    },
                                ),
                                cyto.Cytoscape(
                                    id="cytoscape",
                                    layout={"name": "preset"},
                                    style={
                                        "width": "100%",
                                        "height": "90%",
                                        "color": "red",
                                        "background-color": "white",
                                    },
                                    elements=cyto_graph_elements,
                                    className="border border-light",
                                    stylesheet=[
                                        {
                                            "selector": "edge",
                                            "style": {
                                                "curve-style": "bezier",
                                                "target-arrow-shape": "vee",
                                            },
                                        },
                                        {
                                            "selector": "node",
                                            "style": {"label": "data(id)"},
                                        },
                                    ],
                                ),
                            ],
                            style={
                                "width": "100%",
                                "height": "90%",
                            },
                        ),
                    ],
                    style={
                        "width": "100%",
                        "height": "75%",
                        "padding": "5px",
                    },
                    className="bg-body-tertiary card",
                ),
            ],
            style={
                "display": "flex",
                "flexDirection": "column",
                "width": "100%",
                "height": "100%",
            },
            className="bg-dark",
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "width": "50%",
        "padding": "10px",
        "padding-right": "2.5px",
    },
)

sidebar = html.Div(
    [
        html.H2("OTEL 2 PUML", className="navbar-brand text-light-emphasis"),
        html.Hr(),
        html.P(
            "An OpenTelemetry Discovery App",
            className="lead text-body-tertiary",
        ),
        dbc.Nav(
            [
                dbc.NavLink(
                    "Home",
                    href="/",
                    active="exact",
                ),
                dbc.NavLink("Visualisations", href="/page-1", active="exact"),
            ],
            vertical=True,
        ),
    ],
    style=SIDEBAR_STYLE,
    className="bg-body-tertiary",
)

plantuml_output_content = html.Div(
    children=[
        html.Div(
            [
                html.H3(
                    "PlantUML Output",
                    className="text-center bg-body-tertiary "
                    "text-body-tertiary",
                    style={
                        "width": "90%",
                        "margin-left": "auto",
                        "margin-right": "auto",
                        "height": "10%",
                        "margin-top": "auto",
                        "margin-bottom": "auto",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Img(
                                    src="data:image/svg+xml;base64,{}".format(
                                        base64.b64encode(
                                            open(image_filename, "rb").read()
                                        ).decode()
                                    ),
                                    className="d-block user-select-none",
                                    id="puml-image",
                                    style={
                                        "width": "auto",
                                        "height": "auto",
                                        "margin-left": "auto",
                                        "margin-right": "auto",
                                        "margin-top": "auto",
                                        "margin-bottom": "auto",
                                        "max-width": "100%",
                                    },
                                )
                            ],
                            style={
                                "overflow": "scroll",
                                "width": "100%",
                                "height": "100%",
                                "margin-left": "auto",
                                "margin-right": "auto",
                                "margin-top": "auto",
                                "margin-bottom": "auto",
                            },
                            className="bg-body-tertiary",
                        )
                    ],
                    style={"width": "100%", "height": "90%"},
                ),
            ],
            style={
                "display": "flex",
                "flexDirection": "column",
                "width": "100%",
                "height": "100%",
                "padding": "5px",
            },
            className="bg-body-tertiary card",
        )
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "width": "50%",
        "padding": "10px",
        "padding-left": "2.5px",
    },
)

content = html.Div(
    children=[
        cyto_content,
        plantuml_output_content,
    ],
    style={
        "display": "flex",
        "flexDirection": "row",
        "height": "100vh",
        "width": "100%",
    },
    className="bg-dark",
)


app.layout = html.Div(
    [
        html.Div(
            [sidebar],
            style={
                "display": "flex",
                "flexDirection": "row",
                "height": "100%",
                "width": "200px",
                "flex-shrink": "0",
            },
        ),
        html.Div(
            [content],
            style={
                "display": "flex",
                "flexDirection": "row",
                "height": "100%",
                "flex": "1",
            },
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "row",
        "height": "100vh",
        "width": "100%",
    },
)


@callback(
    Output("cytoscape", "elements", allow_duplicate=True),
    Output("drop_down_for_graphs", "options"),
    Input("pandas-dropdown-2", "value"),
    prevent_initial_call=True,
)
def update_cyto_for_first_entry(value) -> list[dict]:
    """Update the cytoscape graph for the first entry"""
    if value not in folder_names_and_paths:
        raise dash.exceptions.PreventUpdate
    folder_path = folder_names_and_paths[value]
    cyto_graph_elements.clear()
    cyto_graph_elements.extend(get_cytos_from_folder_of_pv_job(folder_path))
    return cyto_graph_elements[0], list(range(len(cyto_graph_elements)))


@callback(
    Output("pandas-dropdown-2", "options"),
    Input("my-dropdown-parent", "n_clicks"),
)
def change_my_dropdown_options(n_clicks) -> list:
    """Change the options of the drop down"""
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    for folder_name in os.listdir(input_data_folder_path):
        folder_path = os.path.join(input_data_folder_path, folder_name)
        if os.path.isdir(folder_path):
            folder_names_and_paths[folder_name] = folder_path
    return list(folder_names_and_paths.keys())


@callback(
    Output("puml-image", "src"),
    Input("run-button", "n_clicks"),
    State("pandas-dropdown-2", "value"),
    prevent_initial_call=True,
)
def update_puml_image(n_clicks, value) -> str:
    """Update the PlantUML image from the drop down"""
    puml_path = f"{value}.puml"
    pv_jobs_from_folder_to_puml_file(
        folder_names_and_paths[value], puml_path, keep_dummy_events=True
    )
    return_code = os.system(
        f"java -jar {plantuml_jar_path} {puml_path} -tsvg"
    )
    if return_code != 0:
        raise dash.exceptions.PreventUpdate
    image_filename = f"{value}.svg"
    encoded_image = base64.b64encode(
        open(image_filename, "rb").read()
    ).decode()
    return f"data:image/svg+xml;base64,{encoded_image}"


def get_network_x_graphs_from_folder_of_pv_job(
    folder_path: str,
) -> Generator[nx.DiGraph, Any, None]:
    """Get a list of networkx graphs from a folder of PV job json files"""
    pv_stream = pv_jobs_from_folder_to_event_sequence_streams(folder_path)
    graph_solutions = get_graph_solutions_from_clustered_events(pv_stream)
    for graph_solution in graph_solutions:
        nx_graph = nx.DiGraph()
        for event in graph_solution.events.values():
            for post_event in event.post_events:
                nx_graph.add_edge(str(event), str(post_event))
        yield nx_graph


def get_cyto_from_nx_graph(nx_graph: nx.DiGraph) -> list[dict]:
    """Get a list of cytoscape elements from a networkx graph"""
    pos = nx.nx_agraph.graphviz_layout(nx_graph, prog="dot")
    elements = []
    for node in nx_graph.nodes:
        elements.append(
            {
                "data": {"id": str(node), "label": str(node)},
                "position": {"x": pos[node][0], "y": pos[node][1]},
            }
        )
    edges = set()
    for edge in nx_graph.edges:
        edge = (str(edge[0]), str(edge[1]))
        if edge in edges:
            continue
        elements.append(
            {"data": {"source": str(edge[0]), "target": str(edge[1])}}
        )
    return elements


def get_cytos_from_folder_of_pv_job(
    folder_path: str,
) -> Generator[list[dict], Any, None]:
    """Get a list of cytoscape elements from a folder of PV job json files"""
    saved_graphs = []
    for network_x_graph in get_network_x_graphs_from_folder_of_pv_job(
        folder_path
    ):
        if any(
            nx.is_isomorphic(network_x_graph, saved_graph)
            for saved_graph in saved_graphs
        ):
            continue
        saved_graphs.append(network_x_graph)
        yield get_cyto_from_nx_graph(network_x_graph)


@callback(
    Output("cytoscape", "elements", allow_duplicate=True),
    Input("drop_down_for_graphs", "value"),
    prevent_initial_call=True,
)
def update_cyto_from_drop_down(value) -> list[dict]:
    """Update the cytoscape graph from the drop down"""
    if value is None:
        raise dash.exceptions.PreventUpdate
    return cyto_graph_elements[value]


@callback(
    Output("cytoscape", "elements", allow_duplicate=True),
    Input("reset-axes", "n_clicks"),
    State("drop_down_for_graphs", "value"),
    prevent_initial_call=True,
)
def reset_axes(n_clicks, value) -> list[dict]:
    """Reset the axes of the cytoscape graph"""
    if value is None:
        if len(cyto_graph_elements) == 0:
            raise dash.exceptions.PreventUpdate
        value = 0
    return cyto_graph_elements[value]


if __name__ == "__main__":
    app.run_server(debug=True)
