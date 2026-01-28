import dash
from dash import dcc, html

dash.register_page(__name__, path="/help")

layout = html.Div(
    className="help-page-container",
    children=[
        html.H1("Help", className="help-title"),
        html.Div(
            children=[
                # Section Upload data
                html.Div(
                    children=[
                        html.H2("Upload data", className="help-subtitle"),
                        html.Hr(),
                        html.Div(
                            children=[
                                html.H3("Climatic Parameters and Graph section"),
                                dcc.Markdown(
                                    """In this section, you have the option to select the data you want to analyze on the x-axis and y-axis. This allows you to determine how to analyze your data effectively. You can also visualize the selected data on the map to highlight specific information of interest.""",
                                    className="help-text",
                                ),
                                dcc.Markdown(
                                    """To get started, use the drop-down menus to choose the relevant data for both the x-axis and y-axis. Once you've made your selections, the system will generate a graphical representation of your data, making it easier to interpret and identify patterns or trends.
                        The "Bootstrap value threshold" is an important criterion in the interpretation of phylogenetic trees as it helps determine which branches are statistically significant and therefore reliable in representing the evolutionary relationships between the studied species or sequences.""",
                                    className="help-text",
                                ),
                                dcc.Markdown(
                                    """In addition to constructing phylogenetic trees, we also offer a pre-analysis feature for your uploaded data. This pre-analysis allows you to compare your data using different line graphs, histograms, etc. This can be immensely helpful in gaining insights into your data before proceeding with the construction of your phylogenetic trees.""",
                                    className="help-text",
                                ),
                                dcc.Markdown(
                                    """Using line graphs, you can visualize the variations in your data over time, while histograms can help you understand the distribution of your data and identify potential clusters.
                        By combining these approaches, you can gain a better understanding of relationships between your data, which may influence your decisions when constructing phylogenetic trees. This will empower you to have a more comprehensive grasp of your data and make well-informed choices during your analyses.
                            """,
                                    className="help-text",
                                ),
                            ]
                        ),
                    ],
                    className="help-sections",
                ),
                # Section Check results
                html.Div(
                    children=[
                        html.H2("Check results", className="help-subtitle"),
                        html.Hr(),
                        dcc.Markdown(
                            """
                            The Results page displays the outcome of your phylogenetic analysis. Here you can verify and explore the generated trees and data.

                            Phylogenetic Trees:
                            - Climatic Trees: Visualizations based on the climatic data provided.
                            - Genetic Trees: Visualizations based on the genetic sequences aligned.

                            Data Visualization:
                            - A graph is displayed showing the Bootstrap mean and Distance relative to the position in the ASM (Aligned Sequence Map).
                            - You can interact with these graphs to analyze specific regions of your data.

                            Downloads:
                            You can examine and download the following outputs:
                            - Aligned genetic sequences: Available as a JSON file.
                            - Genetic and Climatic Trees: Available in Newick format for use with tree viewing software.
                            - Complete Results: A CSV file containing the full analysis output.
                            """,
                            className="help-text",
                        ),
                    ],
                    className="help-sections",
                ),
                # Section Settings
                html.Div(
                    children=[
                        html.H2("Settings", className="help-subtitle"),
                        html.Hr(),
                        dcc.Markdown(
                            """
                            The Settings page allows you to fine-tune the parameters used for the genetic analysis algorithms.

                            Genetic Parameters:
                            - Bootstrap threshold: Set the minimum bootstrap value for branch reliability (0-100).
                            - Distance threshold: Defines the cutoff for genetic distance calculations.
                            - Window size & Step size: Configure the sliding window approach for sequence analysis.
                            - Similarity rate: Set the threshold for sequence similarity.

                            Methods & Algorithms:
                            - Alignment Method: Choose the algorithm for sequence alignment.
                            - Distance Method: Select the method for calculating genetic distances.
                            - Fit Method: Choose how the model fits the data.
                            - Tree Type: Select the library or method for tree construction.
                            """,
                            className="help-text",
                        ),
                    ],
                    className="help-sections",
                ),
            ]
        ),
    ],
)
