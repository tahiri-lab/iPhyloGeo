from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from dash import callback
import dash

dash.register_page(__name__, path='/')

external_stylesheets = [
    {
        'href': 'https://use.fontawesome.com/releases/v6.1.1/css/all.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
        'crossorigin': 'anonymous'
    }
]

layout = html.Div([
    html.Div(
        className="home-page",
        children=[
            html.Div(id='backgroud-video'),
            html.Div(
                className="main-text",
                children=[
                    html.Div('Welcome to the Tahiri Lab', className="title"),
                    html.Div(['We are a dynamic research group at the Sherbrooke University, Department of Computer Science. ',
                              html.A(['Learn more',
                                      html.ObjectEl(id='icon', data='../assets/icons/up-right-from-square-solid.svg', type="image/svg+xml", className='icon')
                                      ], target='_blank', href='https://tahirinadia.github.io/', className="url"),
                              ], className="sub-title"),
                    dbc.NavLink("Get Started", href='/getStarted', id='themes', className="button primary", active="exact"),
                ]
            ),
        ]
    ),
])


@callback(
    Output('backgroud-video', 'children'),
    Input('theme-switch-output', 'children')
)
def update_background_video(children):
    """
    Update the background video according to the theme
    args:
        children: the theme
    return:
        the background video
    """
    if children is False:
        return html.Div(
            children=[
                html.Video(src='../assets/videos/indexPhylogeo_light.mp4', autoPlay=True, loop=True, muted=True, controls=False, className="home-page__video"),
            ]),
    else:
        return html.Video(src='../assets/videos/indexPhylogeo.mp4', autoPlay=True, loop=True, muted=True, controls=False, className="home-page__video"),
