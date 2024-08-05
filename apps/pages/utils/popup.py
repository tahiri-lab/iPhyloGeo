from dash import html, dcc

layout = html.Div([
    html.Div(
        html.Div([
            html.Div([
                html.Div('Your results are on the way!', className="title"),
                html.A([
                    html.Img(src='../../assets/img/coffee-cup.gif', className="icon"),
                ], href="https://www.flaticon.com/authors/freepik", target="_blank", className="link"),
                html.Div('This may take a few minutes.', className="description"),
                html.Div('Another popup will show when results are done.', className="description"),
                # Input para el correo y botón de envío
                html.Div([
                    dcc.Input(id='email-input', type='email', placeholder='Enter your email...'),
                    html.Button('Send Email', id='send-email-button', n_clicks=0),
                ], className='email-container')
            ], className='content'),
        ], className="popup hidden", id="popup")
    ),
])
