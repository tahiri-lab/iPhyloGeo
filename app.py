import dash
import dash_bootstrap_components as dbc
import pandas as pd

FONT_AWESOME = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
)

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB, FONT_AWESOME], #https://bootswatch.com/default/
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                    )
server = app.server


#output_df = pd.read_csv("output.csv")