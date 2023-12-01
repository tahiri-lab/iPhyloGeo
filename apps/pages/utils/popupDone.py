from dash import html

layout = html.Div([
    html.Div(
        html.Div([
            html.Div([
                # html.Div([
                #     html.Img(src='../../assets/icons/close.svg', className="icon", id="close_popup"),
                # ], className="close"),
                html.Div('Results completed!', className="title"),
                html.A('Go to results page', href="/results", className="description"),
            ], className='content'),
        ], className="popup hidden", id="popupDone")
    ),
])
