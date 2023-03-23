import dash
import dash_bootstrap_components as dbc
from flask import Flask

from db import db_validator

FONT_AWESOME = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
)

server = Flask(__name__)

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB, FONT_AWESOME], #https://bootswatch.com/default/
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                server=server)

mongo_client = db_validator.connect_db(app)

files_db = mongo_client.db.Files
results_db = mongo_client.db.Results

# ENV_CONFIG = {
#     'APP_ENV': os.environ.get('APP_ENV', 'local'),
# }