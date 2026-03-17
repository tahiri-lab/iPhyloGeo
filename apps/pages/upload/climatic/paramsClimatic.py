import dash
import pandas as pd
import plotly.express as px
import utils.utils as utils
from dash import Input, Output, State, callback, dash_table, dcc, html

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Sample DataFrame for demonstration
df = pd.DataFrame({"A": [1, 2, 3, 4], "B": [10, 20, 30, 40], "C": [100, 200, 300, 400]})


def create_table(df):
    param_selection = html.Div(
        [
            dcc.Store(id="figures", data=[], storage_type="memory"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div("Data Preview", className="table-title"),
                                    dash_table.DataTable(
                                        id="datatable-interactivity",
                                        data=df.to_dict("records"),
                                        columns=[
                                            {"name": i, "id": i} for i in df.columns
                                        ],
                                        filter_action="native",
                                        sort_action="native",
                                        sort_mode="single",
                                        page_current=0,
                                        page_size=15,
                                        filter_query="",
                                        **utils.get_table_styles(),
                                    ),
                                    dcc.Store(
                                        id="stored-data", data=df.to_dict("records")
                                    ),
                                ],
                                className="params-climatic-table",
                            ),
                            html.Div(id="filter-container"),
                            html.Div(
                                [
                                    html.Div(
                                        "Generate your graph",
                                        className="graph-section-title",
                                    ),
                                    # X and Y axis dropdowns side by side
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.P(
                                                        "Insert X axis data",
                                                        className="field-label",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="xaxis-data",
                                                        options=[],
                                                        className="axis-dropdown",
                                                    ),
                                                ],
                                                className="axis-field-item",
                                            ),
                                            html.Div(
                                                [
                                                    html.P(
                                                        "Insert Y axis data",
                                                        className="field-label",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="yaxis-data",
                                                        options=[],
                                                        className="axis-dropdown",
                                                    ),
                                                ],
                                                className="axis-field-item",
                                            ),
                                        ],
                                        className="axis-row",
                                    ),
                                    # Chart type cards
                                    html.P("Chart type", className="field-label"),
                                    dcc.Checklist(
                                        id="choose-graph-type",
                                        options=[
                                            {
                                                "label": html.Span([
                                                    html.Img(
                                                        src="../../assets/icons/chart-bar.svg",
                                                        className="chart-icon",
                                                    ),
                                                    html.Span("Bar graph"),
                                                ]),
                                                "value": "Bar",
                                            },
                                            {
                                                "label": html.Span([
                                                    html.Img(
                                                        src="../../assets/icons/chart-scatter.svg",
                                                        className="chart-icon",
                                                    ),
                                                    html.Span("Scatter plot"),
                                                ]),
                                                "value": "Scatter",
                                            },
                                            {
                                                "label": html.Span([
                                                    html.Img(
                                                        src="../../assets/icons/chart-line.svg",
                                                        className="chart-icon",
                                                    ),
                                                    html.Span("Line plot"),
                                                ]),
                                                "value": "Line",
                                            },
                                            {
                                                "label": html.Span([
                                                    html.Img(
                                                        src="../../assets/icons/chart-pie.svg",
                                                        className="chart-icon",
                                                    ),
                                                    html.Span("Pie plot"),
                                                ]),
                                                "value": "Pie",
                                            },
                                        ],
                                        value=[],
                                        className="chart-type-cards",
                                    ),
                                    # Choropleth map dropdown
                                    html.Div(
                                        [
                                            html.P(
                                                "Select data for choropleth map",
                                                className="field-label",
                                            ),
                                            dcc.Dropdown(
                                                id="map-data",
                                                options=[],
                                                className="axis-dropdown",
                                            ),
                                        ],
                                        className="map-field",
                                    ),
                                ],
                                className="params-climatic-parameters",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        id="output-graph", className="generated-graph"
                                    ),
                                ],
                                className="graph-generator-container",
                            ),
                        ],
                        className="params-climatic",
                    ),
                ],
                className="parameters-section-inside",
            ),
        ],
        className="parameters-section",
        id="climatic_params_section",
    )

    return param_selection


@callback(
    Output("xaxis-data", "options"),
    Output("yaxis-data", "options"),
    Output("map-data", "options"),
    Output("col-analyze", "options"),
    Input("datatable-interactivity", "data"),
)
def update_dropdown_options(rows):
    if not rows:
        return [], [], [], []

    df = pd.DataFrame(rows)
    options = [{"label": col, "value": col} for col in df.columns]
    numeric_options = [
        {"label": col, "value": col} for col in df.select_dtypes(include="number").columns
    ]
    return options, options, options, numeric_options


@callback(
    Output("datatable-interactivity", "columns"),
    Input("xaxis-data", "value"),
    Input("yaxis-data", "value"),
    State("stored-data", "data"),
)
def update_table_columns(x_data, y_data, data):
    if not x_data and not y_data:
        columns = [{"name": i, "id": i} for i in pd.DataFrame(data).columns]
    else:
        selected_columns = [col for col in [x_data, y_data] if col]
        columns = [{"name": i, "id": i} for i in selected_columns]
    return columns


@callback(
    Output("output-graph", "children"),
    Output("figures", "data"),
    Input("choose-graph-type", "value"),
    Input("stored-data", "data"),
    Input("xaxis-data", "value"),
    Input("yaxis-data", "value"),
    State("figures", "data"),
)
def make_graphs(graph_types, filter_query, x_data, y_data, figures):
    if not graph_types or not x_data or not y_data:
        empty_message = html.Div(
            "Please select X and Y axis data and at least one chart type to generate a graph",
            className="empty-graph-message"
        )
        return [empty_message], []

    df = pd.DataFrame(filter_query)

    figures.clear()  # Clear existing figures

    for graph_type in graph_types:
        if graph_type == "Bar":
            fig = px.bar(df, x=x_data, y=y_data)
        elif graph_type == "Scatter":
            fig = px.scatter(df, x=x_data, y=y_data)
        elif graph_type == "Line":
            fig = px.line(df, x=x_data, y=y_data)
        elif graph_type == "Pie":
            fig = px.pie(df, values=y_data, names=x_data, labels=x_data)

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="var(--reverse-black-white-color)"),
        )
        fig.update_annotations(font_color="white")
        figures.append(dcc.Graph(figure=fig))

    return figures, figures


@callback(
    Output("output-map", "children"),
    Input("map-data", "value"),
    State("datatable-interactivity", "data"),
)
def update_output(map_data, data):
    if not map_data or not data:
        return dash.no_update

    df = pd.DataFrame(data)

    if "iso_alpha" not in df.columns:
        map_fig = html.Div([html.Div("No map to display.")], className="noMapAvailable")
        return map_fig

    fig = px.choropleth(
        df,
        locations="iso_alpha",
        scope="world",
        color=map_data,
        projection="natural earth",
        color_continuous_scale=px.colors.sequential.Turbo,
    )

    fig.update_geos(
        showocean=True,
        oceancolor="LightBlue",
        showlakes=True,
        lakecolor="Blue",
        showrivers=True,
        rivercolor="Blue",
    )

    fig.update_layout(
        title=dict(font=dict(size=28), x=0.5, xanchor="center"),
        margin=dict(l=60, r=60, t=50, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    fig.update_annotations(text="No matching data found")

    # Adjust height and width of the figure
    fig.update_layout(height=500, width=800)

    return dcc.Graph(figure=fig)


app.layout = html.Div([create_table(df)])

if __name__ == "__main__":
    app.run_server(debug=True)
