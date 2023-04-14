from dash import dcc, html, State, Input, Output, dash_table, callback
import dash
import plotly.express as px


figures = []


def create_table(df):
    param_selection = html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dash_table.DataTable(
                        id='datatable-interactivity',
                        data=df.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in df.columns],
                        filter_action="native",  # allow filtering of data by user ('native') or not ('none')
                        sort_action="native",  # enables data to be sorted per-column by user or not ('none')
                        sort_mode="single",  # sort across 'multi' or 'single' columns
                        page_current=0,  # page number that user is on
                        page_size=15,  # number of rows visible per page
                        filter_query='',  # query that determines which rows to keep in table
                        style_data={
                            'color': 'var(--reverse-black-white-color)',
                            'backgroundColor': 'var(--table-bg-color'
                        },
                    ),
                    dcc.Store(id='stored-data', data=df.to_dict('records')),
                ], className="params-climatic-table"),
                html.Div(id='filter-container'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div('Generate your graph', className="title"),
                            html.Div([
                                html.P("Insert X axis data"),
                                dcc.Dropdown(id='xaxis-data',
                                             options=[{'label': x, 'value': x} for x in df.columns]),
                            ], className="field"),
                            html.Div([
                                html.P("Insert Y axis data"),
                                dcc.Dropdown(id='yaxis-data',
                                             options=[{'label': x, 'value': x} for x in df.columns]),
                            ], className="field"),
                            dcc.RadioItems(id='choose-graph-type',
                                           options=[
                                               {'label': 'Bar Graph', 'value': 'Bar'},
                                               {'label': 'Scatter Plot', 'value': 'Scatter'},
                                               {'label': 'Line Plot', 'value': 'Line'},
                                               {'label': 'Pie Plot', 'value': 'Pie'}
                                           ], value='Bar', className="field graphType"),
                            html.Div([
                                html.P("Select data for choropleth map"),
                                dcc.Dropdown(id='map-data',
                                             options=[{'label': x, 'value': x} for x in df.columns]),
                            ], className="field"),
                            html.Button(id="submit-button-graph", className='button', children="Create Graph"),
                        ], className="axis-field"),
                        html.Div([
                            html.Div(id='output-map', className="choropleth-map"),
                        ], className="choropleth-map-container"),
                    ], className="axis"),
                ], className="params-climatic-parameters"),
                html.Div([
                    html.Div(id='output-graph', className="generated-graph"),
                ], className="graph-generator-container"),
                html.Div([
                    html.Div(children=[], id='column-error-message'),
                    html.Div([
                        html.Div("Select the name of the column to analyze"),
                        dcc.Checklist(id='col-analyze',
                                      options=[{'label': x, 'value': x} for x in df._get_numeric_data().columns],
                                      labelStyle={'display': 'inline-block', 'marginRight': '20px'}
                                      ),
                    ], className="axis")
                ], className="col-to-analyse-container")
            ], className="params-climatic"),
        ], className="parameters-section-inside"),
    ], className="parameters-section", id="climatic_params_section")

    return param_selection


@callback(
        Output('output-graph', 'children'),
        Input('submit-button-graph', 'n_clicks'),
        State('choose-graph-type', 'value'),
        State('stored-data', 'data'),
        State('xaxis-data', 'value'),
        State('yaxis-data', 'value')
)
def make_graphs(n, graph_type, filter_query, x_data, y_data):
    """

    args :
        n :
        graph_type :
        filter_query :
        x_data :
        y_data :
    returns :

    """
    
    if n is None:
        return dash.no_update
    
    if graph_type == 'Bar':
        fig = px.bar(filter_query, x=x_data, y=y_data)
    if graph_type == 'Scatter':
        fig = px.scatter(filter_query, x=x_data, y=y_data)
    if graph_type == 'Line':
        fig = px.line(filter_query, x=x_data, y=y_data)
    if graph_type == 'Pie':
        fig = px.pie(filter_query, values=y_data, names=x_data, labels=x_data)
    figures.append(dcc.Graph(figure=fig))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='var(--reverse-black-white-color)')),
    fig.update_annotations(font_color='white'),

    return figures


@callback(
    Output('output-map', 'children'),
    Input('upload-data', 'contents'),
    State('datatable-interactivity', 'data'),
    State('map-data', 'value')
)
def update_output(num_clicks, data, val_selected):
    """
    
    args :
        num_clicks : 
        data : 
        val_selected : 
    returns :

    """
    if num_clicks is None:
        return dash.no_update
    
    if "iso_alpha" not in data[0].keys():
        map_fig = html.Div([
            html.Div("No map to display.")
        ], className="noMapAvailable")
        return map_fig

    fig = px.choropleth(data, locations="iso_alpha", scope="world",
                        color=val_selected,
                        projection='natural earth',
                        color_continuous_scale=px.colors.sequential.Turbo)

    fig.update_geos(
        showocean=True, oceancolor="LightBlue",
        showlakes=True, lakecolor="Blue",
        showrivers=True, rivercolor="Blue"
    )

    fig.update_layout(title=dict(font=dict(size=28), x=0.5, xanchor='center'),
                        margin=dict(l=60, r=60, t=50, b=50), paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'),

    fig.update_annotations(text="No matching data found")

    return dcc.Graph(figure=fig)
    
# Button to extract all graphs to a pdf using js https://community.plotly.com/t/exporting-multi-page-dash-app-to-pdf-with-entire-layout/37953/3 ++
