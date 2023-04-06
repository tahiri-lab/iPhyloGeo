from dash import dcc, html, State, Input, Output, callback

layout = html.Div([
    html.Div(
        html.Div([
            html.Div([
                html.Div('Please don\'t close your browser window until we finish generating your file', className="title"),
                html.A([
                    html.Img(src='../../assets/img/coffee-cup.gif', className="icon"),
                ], href="https://www.flaticon.com/authors/freepik", target="_blank", className="link"),
                html.Div('This may take a few minutes', className="description"),
            ], className='content'),
        ], className="popup")
    ),
])