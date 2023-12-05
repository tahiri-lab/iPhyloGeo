from dash import html
import dash
from dash import dcc

dash.register_page(__name__, path='/help')

layout = html.Div(className="help-page-container", children=[
    html.H1("Aide", className='help-title'),

    # Ajout d'une marge à gauche pour déplacer tout le contenu vers la droite
    html.Div(children=[
        # Section Upload data
        html.Div(children=[
            html.H2("Upload data", className='help-subtitle'),
            html.Hr(),
            html.Div(children=[
                html.H3("Climatic Parameters and Graph section"),
                dcc.Markdown('''In this section, you have the option to select the data you want to analyze on the x-axis and y-axis. This allows you to determine how to analyze your data effectively. You can also visualize the selected data on the map to highlight specific information of interest.''', className='help-text'),
                dcc.Markdown('''To get started, use the drop-down menus to choose the relevant data for both the x-axis and y-axis. Once you've made your selections, the system will generate a graphical representation of your data, making it easier to interpret and identify patterns or trends.
                        The "Bootstrap value threshold" is an important criterion in the interpretation of phylogenetic trees as it helps determine which branches are statistically significant and therefore reliable in representing the evolutionary relationships between the studied species or sequences.''', className='help-text'),
                dcc.Markdown('''In addition to constructing phylogenetic trees, we also offer a pre-analysis feature for your uploaded data. This pre-analysis allows you to compare your data using different line graphs, histograms, etc. This can be immensely helpful in gaining insights into your data before proceeding with the construction of your phylogenetic trees.''', className='help-text'),
                dcc.Markdown('''Using line graphs, you can visualize the variations in your data over time, while histograms can help you understand the distribution of your data and identify potential clusters.
                        By combining these approaches, you can gain a better understanding of relationships between your data, which may influence your decisions when constructing phylogenetic trees. This will empower you to have a more comprehensive grasp of your data and make well-informed choices during your analyses.
                            ''', className='help-text')
            ]),
        ], className="help-sections"), 

        # Section Check results
        html.Div(children=[
            html.H2("Check results", className='help-subtitle'),
            html.Hr(),
            dcc.Markdown('''
            Expliquez ici comment accéder et interpréter les résultats de l'analyse.
            ''', className='help-text'),
        ], className="help-sections"),

        # Section Settings
        html.Div(children=[
            html.H2("Settings", className='help-subtitle'),
            html.Hr(),
            dcc.Markdown('''
            Expliquez ici comment utiliser la page des paramètres pour configurer l'application.
            ''', className='help-text'),
        ], className="help-sections"),

        # Ajout d'images
        # html.Div(children=[
        #     html.H2("Images", className='help-subtitle'),  # Style pour mettre en blanc et en gras
        #     html.Img(src='url_de_votre_image_1.png', style={'width': '50%', 'margin-top': '20px'}),  # Ajout de la marge pour déplacer l'image vers la droite
        #     html.Img(src='url_de_votre_image_2.png', style={'width': '50%', 'margin-top': '20px'}),  # Ajout de la marge pour déplacer l'image vers la droite
        # ]),
    ]),
])
