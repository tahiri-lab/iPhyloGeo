from dash import dcc, html, dash_table, callback, Input, Output, State
import dash
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)

# Sample DataFrame for demonstration
df = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [10, 20, 30, 40],
    'C': [100, 200, 300, 400]
})

def create_table(df):
    param_selection = html.Div([
        dcc.Store(id='figures', data=[], storage_type='memory'),
        html.Div([
            html.Div([
                html.Div([
                    dash_table.DataTable(
                        id='datatable-interactivity',
                        data=df.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in df.columns],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="single",
                        page_current=0,
                        page_size=15,
                        filter_query='',
                        style_data={
                            'color': 'var(--reverse-black-white-color)',
                            'backgroundColor': 'var(--table-bg-color)'
                        },
                    ),
                    dcc.Store(id='stored-data', data=df.to_dict('records')),
                ], className="params-climatic-table"),
                html.Div(id='filter-container'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div('Generate your graph', className="title center-text"),
                            html.Div([
                                html.P("Insert X axis data", className='sub-title center-text'),
                                dcc.Dropdown(id='xaxis-data', options=[], className='center-text'),
                            ], className="field"),
                            html.Div([
                                html.P("Insert Y axis data", className='sub-title center-text'),
                                dcc.Dropdown(id='yaxis-data', options=[], className='center-text'),
                            ], className="field"),
                            dcc.Checklist(id='choose-graph-type',
                                           options=[
                                               {'label': 'Bar Graph', 'value': 'Bar'},
                                               {'label': 'Scatter Plot', 'value': 'Scatter'},
                                               {'label': 'Line Plot', 'value': 'Line'},
                                               {'label': 'Pie Plot', 'value': 'Pie'}
                                           ], value=[], className="field graphType center-text"),
                            html.Div([
                                html.P("Select data for choropleth map", className='sub-title center-text'),
                                dcc.Dropdown(id='map-data', options=[], className='center-text'),
                            ], className="field"),
                        ], className="axis-field"),
                    ], className="axis"),
                ], className="params-climatic-parameters"),
                html.Div([
                    html.Div(id='output-graph', className="generated-graph"),
                ], className="graph-generator-container"),
                html.Div([
                    html.Div(children=[], id='column-error-message'),
                    html.Div([
                        html.Div("Select the name of the column to analyze", className='sub-title center-text'),
                        dcc.Checklist(id='col-analyze',
                                      options=[{'label': x, 'value': x} for x in df._get_numeric_data().columns],
                                      labelStyle={'display': 'inline-block', 'marginRight': '20px'},
                                      className='center-text'
                                      ),
                    ], className="axis")
                ], className="col-to-analyse-container")
            ], className="params-climatic"),
        ], className="parameters-section-inside"),
    ], className="parameters-section", id="climatic_params_section")

    return param_selection


@callback(
    Output('xaxis-data', 'options'),
    Output('yaxis-data', 'options'),
    Output('map-data', 'options'),
    Input('datatable-interactivity', 'data')
)
def update_dropdown_options(rows):
    if not rows:
        return [], [], []
    
    df = pd.DataFrame(rows)
    options = [{'label': col, 'value': col} for col in df.columns]
    return options, options, options


@callback(
    Output('datatable-interactivity', 'columns'),
    Input('xaxis-data', 'value'),
    Input('yaxis-data', 'value'),
    State('stored-data', 'data')
)
def update_table_columns(x_data, y_data, data):
    if not x_data and not y_data:
        columns = [{'name': i, 'id': i} for i in pd.DataFrame(data).columns]
    else:
        selected_columns = [col for col in [x_data, y_data] if col]
        columns = [{'name': i, 'id': i} for i in selected_columns]
    return columns


@callback(
    Output('output-graph', 'children'),
    Output('figures', 'data'),
    Input('choose-graph-type', 'value'),
    Input('stored-data', 'data'),
    Input('xaxis-data', 'value'),
    Input('yaxis-data', 'value'),
    State('figures', 'data')
)
def make_graphs(graph_types, filter_query, x_data, y_data, figures):
    if not graph_types or not x_data or not y_data:
        return dash.no_update, dash.no_update

    df = pd.DataFrame(filter_query)
    
    figures.clear()  # Clear existing figures
    
    for graph_type in graph_types:
        if graph_type == 'Bar':
            fig = px.bar(df, x=x_data, y=y_data)
        elif graph_type == 'Scatter':
            fig = px.scatter(df, x=x_data, y=y_data)
        elif graph_type == 'Line':
            fig = px.line(df, x=x_data, y=y_data)
        elif graph_type == 'Pie':
            fig = px.pie(df, values=y_data, names=x_data, labels=x_data)

        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='var(--reverse-black-white-color)'))
        fig.update_annotations(font_color='white')
        figures.append(dcc.Graph(figure=fig))
    
    return figures, figures


@callback(
    Output('output-map', 'children'),
    Input('map-data', 'value'),
    State('datatable-interactivity', 'data')
)
def update_output(map_data, data):
    if not map_data or not data:
        return dash.no_update

    df = pd.DataFrame(data)

    if "iso_alpha" not in df.columns:
        map_fig = html.Div([
            html.Div("No map to display.")
        ], className="noMapAvailable")
        return map_fig

    fig = px.choropleth(df, locations="iso_alpha", scope="world",
                        color=map_data,
                        projection='natural earth',
                        color_continuous_scale=px.colors.sequential.Turbo)

    fig.update_geos(
        showocean=True, oceancolor="LightBlue",
        showlakes=True, lakecolor="Blue",
        showrivers=True, rivercolor="Blue"
    )

    fig.update_layout(title=dict(font=dict(size=28), x=0.5, xanchor='center'),
                      margin=dict(l=60, r=60, t=50, b=50), paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    fig.update_annotations(text="No matching data found")
   
    # Adjust height and width of the figure
    fig.update_layout(height=500, width=800)

    return dcc.Graph(figure=fig)


app.layout = html.Div([
    create_table(df)
])

if __name__ == '__main__':
    app.run_server(debug=True)
