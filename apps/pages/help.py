import dash
from dash import dcc, html
from components.page_section import create_page_section

dash.register_page(__name__, path="/help")

layout = html.Div(
    className="page-container",
    children=[
        html.Div("Help", className="title"),
        html.Div(
            className="page-card",
            children=[
                # Section Upload data
                create_page_section(
                    "Upload data",
                    icon_src="/assets/icons/folder-upload.svg",
                    children=[
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
By combining these approaches, you can gain a better understanding of relationships between your data, which may influence your decisions when constructing phylogenetic trees. This will empower you to have a more comprehensive grasp of your data and make well-informed choices during your analyses.""",
                                    className="help-text",
                                ),
                            ],
                            className="help-section-content",
                        ),
                    ],
                ),
                # Section Check results
                create_page_section(
                    "Check results",
                    icon_src="/assets/icons/eye.svg",
                    children=[
                        html.Div(
                            children=[
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
                            className="help-section-content",
                        ),
                    ],
                ),
                # Section Settings
                create_page_section(
                    "Settings",
                    icon_src="/assets/icons/gears.svg",
                    children=[
                        html.Div(
                            children=[
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
                            className="help-section-content",
                        ),
                    ],
                ),
                # Section Statistical Tests
                create_page_section(
                    "Statistical Tests",
                    icon_src="/assets/icons/flask.svg",
                    children=[
                        html.Div(
                            children=[
                                dcc.Markdown(
                                    """
The application supports two statistical tests to measure the correlation between genetic and climatic distance matrices.

Mantel Test
The Mantel test evaluates the correlation between two distance matrices (e.g., genetic vs. climatic distances).
A high correlation indicates that geographically or climatically similar samples are also genetically similar.
- Method: Choose between *Pearson* (linear correlation) or *Spearman* (rank-based, more robust to outliers).
- Permutations: The number of random permutations used to compute the p-value. More permutations give a more precise p-value, but take longer to compute. Typical values range from 999 to 9999.

PROTEST (Procrustes Test)
PROTEST is a Procrustes-based permutation test that compares two multivariate configurations (ordinations) derived from the distance matrices.
It measures how well one configuration can be rotated, scaled, and translated to match the other.
- m² statistic: Ranges from 0 (perfect fit) to 1 (no fit). A lower m² indicates a stronger concordance between the two matrices.
- Permutations: Same principle as the Mantel test — more permutations yield a more accurate p-value.

Choosing a test
- Use Both to run both tests and get a comprehensive view of the correlation.
- Use Mantel only or PROTEST only if you want to focus on a specific approach or reduce computation time.
""",
                                    className="help-text",
                                ),
                            ],
                            className="help-section-content",
                        ),
                    ],
                ),
            ],
        ),
    ],
)
