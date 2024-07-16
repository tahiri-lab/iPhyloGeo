from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from dash import callback, register_page

register_page(__name__, path='/')

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
            html.Div(id='background-video'),
            html.Div(
                className="main-text",
                children=[
                    html.Div('Welcome to the Tahiri Lab', className="title"),
                    html.Div([
                        'We are a dynamic research group at the Sherbrooke University, Department of Computer Science. ',
                        html.A([
                            'Learn more',
                            html.Img(src='../assets/icons/up-right-from-square-solid.svg', className='icon')
                        ], target='_blank', href='https://tahirinadia.github.io/', className="url"),
                    ], className="sub-title"),
                    dbc.NavLink("Get Started", href='/getStarted', id='themes', className="button primary", active="exact"),
                ]
            ),
        ]
    ),
])

@callback(
    Output('background-video', 'children'),
    Input('theme-switch-output', 'children')
)
def update_background_video(theme):
    """
    Update the background video according to the theme.
    Args:
        theme: the theme indicator
    Returns:
        The background video element.
    """
    if theme is None:
        return []
    
    if not theme:
        return html.Video(
            src='../assets/videos/indexPhylogeo_light.mp4', 
            autoPlay=True, 
            loop=True, 
            muted=True, 
            controls=False, 
            className="home-page__video"
        )

    return html.Video(
        src='../assets/videos/indexPhylogeo.mp4', 
        autoPlay=True, 
        loop=True, 
        muted=True, 
        controls=False, 
        className="home-page__video"
    )
