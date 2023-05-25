
from dash import dcc, html
# import dash_core_components as dcc
# import dash_html_components as html
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from app import app


# get relative data folder
# PATH = pathlib.Path(__file__).parent
# IMG_PATH = PATH.joinpath("../assets").resolve()

# dfg = pd.read_csv(DATA_PATH.joinpath("theData_IfWeHave.csv"))

card1 = dbc.Card(
    [
        dbc.CardImg(src="/assets/UdeS1.jpg", top=True),
        dbc.CardBody(
            [
                html.H4("Welcome to the Tahiri Lab", className="card-title"),
                html.P(
                    "We are a dynamic research group at the Sherbrooke University, Department of Computer Science. ",
                    className="card-text",
                ),
                html.P(
                    "Through engaged scholarship, our laboratory develops transdisciplinary research projects to analyze the"
                    "evolution of species and assess the impacts on health by combining, among other things, information"
                    "from the genetics of species and climatic parameters.",
                    className="card-text",
                ),
                dbc.CardLink(
                    "Tahiri Lab", href="https://tahirinadia.github.io/"),
            ]
        ),
    ],
    # style={"width": "45%"},
),

card2 = dbc.Card(
    [
        dbc.CardImg(src="/assets/workflow.png", top=True),
        dbc.CardBody(
            [
                html.H4("The aPhyloGeo-pipeline analysis workflow",
                        className="card-title"),
                html.P(
                    """
                    The workflow describes the input data (gray), software names, package names, and its versions (green),
                    analysis steps (blue), filter steps (pink) and output files (orange). Snakemake provides options for scalability and optimizes resource usage.
                    """,
                    className="card-text",
                ),
                dbc.CardLink(
                    "Github", href="https://github.com/tahiri-lab/aPhyloGeo-pipeline"),
            ]
        ),
    ],
    # style={"width": "45%"},
),

card3 = dbc.Card(
    [
        dbc.CardImg(src="/assets/SlidingWindows.jpg", top=True),
        dbc.CardBody(
            [
                html.H4("Integrated analysis of genetic data and environmental data",
                        className="card-title"),
                html.P(
                    """
                    The aPhyloGeo-pipeline can analyze both amino acid sequence alignment data and nucleic acid sequence alignment data.
                      By setting the window size and step size, the alignment of multiple sequences was segmented into sliding windows. For each sliding window,
                      Robinson and Foulds distances are computed for every combination of the sliding window of phylogenetic tree and
                      the reference tree created from environmental factors.
                    """,
                    className="card-text",
                ),

            ]
        ),
    ],
    # style={"width": "45%"},
),

card4 = dbc.Card(
    [
        dbc.CardImg(src="/assets/visualisation_schema.png", top=True),
        dbc.CardBody(
            [
                html.H4("The aPhyloGeo-pipeline analysis workflow",
                        className="card-title"),
                html.P(
                    """
                    The workflow describes the input data (gray), software names, package names, and its versions (green),
                    analysis steps (blue), filter steps (pink) and output files (orange). Snakemake provides options for scalability and optimizes resource usage.
                    """,
                    className="card-text",
                ),
                dbc.CardLink(
                    "Github", href="https://github.com/tahiri-lab/iPhyloGeo.js/tree/main"),
            ]
        ),
    ],
    # style={"width": "45%"},
),

# -----------------------------------------
layout = html.Div([
    html.Div(html.H2("Phylogeography"), style={"text-align": "center"}),
    html.Hr(),
    # ----------
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div(card1),
            ], xs=12, sm=12, md=12, lg=4, xl=4),
            dbc.Col([
                html.Div(card2),
            ], xs=12, sm=12, md=12, lg=7, xl=7),

        ], justify='around'),

        html.Br(),
        html.Br(),

        dbc.Row([
            dbc.Col([
                html.Div(card3),
            ], xs=12, sm=12, md=12, lg=4, xl=4),
            dbc.Col([
                html.Div(card4),
            ], xs=12, sm=12, md=12, lg=7, xl=7),

        ], justify='around'),

        # dbc.Row([
        #     dbc.Col([
        #         html.Div(card4),
        #     ], xs=12, sm=12, md=12, lg=12, xl=12),

        # ], justify='around'),

    ], fluid=True),

    # -------
])
