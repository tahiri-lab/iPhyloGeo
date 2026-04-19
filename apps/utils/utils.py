import base64
import io
import json
import os
from datetime import datetime, timezone
from importlib import import_module

import numpy as np

import db.controllers.files as files_ctrl
import db.controllers.results as results_ctrl
import pandas as pd
from aphylogeo.params import Params
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment
from dash import dcc, html
from scipy.spatial.distance import pdist, squareform

COOKIE_NAME = "AUTH"
COOKIE_MAX_AGE = 8640000  # 100 days

_APHYLOGEO_UTILS = None


def _get_aphylogeo_utils():
    global _APHYLOGEO_UTILS
    if _APHYLOGEO_UTILS is None:
        _APHYLOGEO_UTILS = import_module("aphylogeo.utils")
    return _APHYLOGEO_UTILS


def format_card_date(value):
    if value is None:
        return None

    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y")

    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized).strftime("%d/%m/%Y")
        except ValueError:
            return value

    return str(value)


def to_datetime_utc(value):
    min_utc = datetime.min.replace(tzinfo=timezone.utc)

    if value is None:
        return min_utc
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            return min_utc
    return min_utc


def get_all_files():
    """
    Get all files from the database.

    Returns:
        list: List of files.
    """
    return files_ctrl.get_all_files()


def get_results(ids):
    """
    Get the results with the given ids.

    Args:
        ids (list<string>): The ids of the results

    Returns:
        list: List of results.
    """
    return results_ctrl.get_results(ids)


def get_result(id):
    """
    Get one result with the given id.

    Args:
        id (string): The id of the results

    Returns:
        dict: results.
    """
    return results_ctrl.get_result(id)


def get_all_results():
    """
    Get all results.

    Returns:
        list: List of results.
    """
    return results_ctrl.get_all_results()


def save_files(results):
    """
    Save the files to the database.

    Args:
        results (list): List of files.

    Returns:
        list: List of ids of the saved files.
    """
    return files_ctrl.save_files(results)


def get_file(id, options=None):
    """Get the file with the given id from MongoDB.

    Args:
        id (string): The id of the file.
        options (dict, optional): Deprecated. Kept for backward compatibility.
    """
    return get_file_from_db(id)


def get_file_from_db(id):
    """Get the file from the database.

    Args:
        id (string): The id of the file.
    """
    return files_ctrl.get_files_by_id(id)


def get_files_from_base64(list_of_contents, list_of_names, last_modifieds):
    """
    DCC Upload component returns a list of base64 encoded strings.
    This function decodes the strings and parse them.

    Args:
        list_of_contents (list): List of base64 encoded strings.
        list_of_names (list): List of file names.
        last_modifieds (list): List of last modified dates.
    returns:
        list: List of parsed files.
    """
    results = []
    for content, file_name, date in zip(
        list_of_contents, list_of_names, last_modifieds
    ):
        results.append(parse_contents(content, file_name, date))

    return results


def download_file_from_db(id, root_path="./"):
    """Download the file from the database.

    Args:
        id (string): The id of the file.
    """
    res = get_file_from_db(id)

    with open(root_path + res["file_name"], "wb") as f:
        if res["file_name"].endswith(".xlsx"):
            res["df"].to_excel(f, index=False, header=True)
        elif res["file_name"].endswith(".csv"):
            res["df"].to_csv(f, index=False, header=True)
        elif res["file_name"].endswith(".fasta"):
            res["file"] = SeqIO.to_dict(res["file"])
            fasta_str = ""
            for key, seq in res["file"].items():
                fasta_str += f">{key}\n{str(seq.seq)}\n"
            f.write(fasta_str.encode("utf-8"))


def parse_contents(content, file_name, date):
    res = {
        "file_name": file_name,
        "last_modified_date": date,
    }

    try:
        content_type, content_string = content.split(",")
        decoded_content = base64.b64decode(content_string)

        if content_type in [
            "data:text/csv;base64",
            "data:application/vnd.ms-excel;base64",
        ]:
            # Assume that the user uploaded a CSV file
            res["df"] = pd.read_csv(io.StringIO(decoded_content.decode("utf-8")))
            res["type"] = "climatic"
        elif "xls" in file_name:
            # Assume that the user uploaded an excel file
            res["df"] = pd.read_excel(io.BytesIO(decoded_content))
            res["type"] = "climatic"
        elif "fasta" in file_name:
            # res['file'] = SeqIO.parse(io.StringIO(decoded_content.decode('utf-8')), 'fasta')
            res["file"] = files_ctrl.fasta_to_str(
                SeqIO.parse(io.StringIO(decoded_content.decode("utf-8")), "fasta")
            )
            res["type"] = "genetic"
        else:
            res["error"] = True

        return res
    except Exception as e:
        print(e)


def create_seq_html(file):
    file_name = file["file_name"]

    if "error" in file and file["error"]:
        return html.Div(
            [
                dcc.Markdown("Please upload a **fasta file**."),
            ]
        )

    return html.Div(
        [
            dcc.Markdown("You have uploaded file(s):  **{}**".format(file_name)),
        ]
    )


def create_result(
    files_ids,
    result_type,
    climatic_params=None,
    genetic_params=None,
    name="result",
    status="pending",
    temporary=False,
):
    """
    Creates a result in the database.

    Args:
        files_ids: a dictionary with the ids of the files used in the result.
        result_type: an array with the types of the files used in the result.
        climatic_params: json object with the parameters for the climatic pipeline
        genetic_params: json object with the genetic parameters
        name: the name of the result
        status: the status of the result

    Returns:
        The id of the created result.
    """
    try:
        result = {"name": name, "status": status, "result_type": result_type}

        if "climatic_files_id" in files_ids:
            result["climatic_files_id"] = files_ids["climatic_files_id"]
        if "climatic_tree_files_id" in files_ids:
            result["climatic_tree_files_id"] = files_ids["climatic_tree_files_id"]
        if "genetic_files_id" in files_ids:
            result["genetic_files_id"] = files_ids["genetic_files_id"]
        if "aligned_genetic_files_id" in files_ids:
            result["aligned_genetic_files_id"] = files_ids["aligned_genetic_files_id"]
        if "genetic_tree_files_id" in files_ids:
            result["genetic_tree_files_id"] = files_ids["genetic_tree_files_id"]
        if genetic_params and "genetic" in result_type:
            result["genetic_params"] = genetic_params
        if climatic_params and "climatic" in result_type:
            result["climatic_params"] = climatic_params

        if temporary:
            return results_ctrl.create_temp_result(result)

        return results_ctrl.create_result(result)

    except Exception as e:
        print("[Error]:", e)
        raise Exception("Error creating the result")


def create_climatic_trees(
    result_id, climatic_data, selected_columns=None, status="climatic_trees"
):
    """Creates a climatic result.

    If climatic preprocessing is enabled (Params.preprocessing_climatic == '1'),
    two filters are applied before building the trees:
    1. Low-variance filter: removes columns with variance below
       Params.preprocessing_threshold_climatic.
    2. High-correlation filter: iteratively removes the most correlated
       column until no pair exceeds Params.correlation_threshold_climatic
       (Spearman correlation).

    Args:
        result_id (str): the id of the result
        climatic_data: json object with the climatic data
        selected_columns: list of column names to analyze (optional, if None all columns are used)
        status (str, optional): The status of the result. Defaults to 'climatic_trees'.

    Returns:
        climatic_trees: a dictionary with the climatic trees
    """
    try:
        df = pd.read_json(io.StringIO(climatic_data))

        # Filter DataFrame to only include selected columns
        if selected_columns is not None and len(selected_columns) > 0:
            # Ensure the first column (specimen ID) is always included
            columns_to_keep = [df.columns[0]] + [
                c for c in selected_columns if c in df.columns and c != df.columns[0]
            ]
            df = df[columns_to_keep]

        # Climatic preprocessing: remove low-variance feature columns
        id_col = df.columns[0]
        if int(Params.preprocessing_climatic):
            threshold = float(Params.preprocessing_threshold_climatic)
            feature_cols = df.columns[1:]
            variances = df[feature_cols].var()
            cols_to_keep = variances[variances >= threshold].index.tolist()
            df = df[[id_col] + cols_to_keep]

        # Remove highly correlated columns (Spearman) — independent of variance preprocessing
        # correlation_threshold_climatic is an iPhyloGeo-specific setting, not in aphylogeo's Params
        _settings = json.load(open("genetic_settings_file.json", "r"))
        if _settings.get("correlation_climatic_enabled", "0") == "Enabled":
            max_corr_threshold = float(_settings.get("correlation_threshold_climatic", 0.9))
            feature_cols = list(df.columns[1:])
            while True:
                corr_matrix = df[feature_cols].corr(method="spearman").abs()
                upper_tri = corr_matrix.where(
                    np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
                )
                max_corr = upper_tri.max().max()
                if max_corr < max_corr_threshold:
                    break
                # Find the column with the highest mean correlation above threshold
                col_scores = {}
                for col in upper_tri.columns:
                    high = upper_tri[col][upper_tri[col] >= max_corr_threshold]
                    if not high.empty:
                        col_scores[col] = high.mean()
                if col_scores:
                    drop_col = max(col_scores, key=col_scores.get)
                    feature_cols.remove(drop_col)
                else:
                    break
            df = df[[id_col] + feature_cols]

        climatic_trees = _get_aphylogeo_utils().climaticPipeline(df)
        results_ctrl.update_result(
            {
                "_id": result_id,
                "climatic_trees": climatic_trees,
                "status": status,
            }
        )
        return climatic_trees
    except Exception as e:
        print("[Error in create_climatic_trees]:", e)
        results_ctrl.update_result(
            {
                "_id": result_id,
                "status": "error",
            }
        )
        raise Exception("Error creating the climatic trees")


def _filter_alignment_gaps(alignment, threshold):
    """Remove columns from a MultipleSeqAlignment where the gap ratio exceeds threshold.

    Args:
        alignment: a Bio.Align.MultipleSeqAlignment object
        threshold (float): maximum allowed ratio of gaps ('-' or 'N') per column

    Returns:
        MultipleSeqAlignment: filtered alignment with gap-heavy columns removed
    """
    keep_cols = []
    for i in range(alignment.get_alignment_length()):
        column = alignment[:, i]
        gap_count = column.count("-") + column.upper().count("N")
        if (gap_count / len(column)) <= threshold:
            keep_cols.append(i)

    filtered_records = []
    for record in alignment:
        new_seq = "".join(record.seq[i] for i in keep_cols)
        filtered_records.append(
            SeqRecord(Seq(new_seq), id=record.id, description=record.description)
        )
    return MultipleSeqAlignment(filtered_records)


def create_alignement(result_id, genetic_data, status="alignement"):
    """
    Creates the alignement of the genetic data.

    If genetic preprocessing is enabled (Params.preprocessing_genetic == '1'),
    columns with a gap ratio above Params.preprocessing_threshold_genetic are
    removed from each alignment window.

    Args:
        result_id (str): the id of the result
        genetic_data: json object with the genetic data

    Returns:
        msaSet: the alignement
    """
    try:
        # Import lazily to avoid loading deprecated Bio.Application wrappers at app startup.
        from aphylogeo.alignement import AlignSequences

        alignmentObject = AlignSequences(genetic_data).align()
        msaSet = alignmentObject.msa

        # Genetic preprocessing: remove gap-heavy columns from each window
        if int(Params.preprocessing_genetic):
            threshold = float(Params.preprocessing_threshold_genetic)
            filtered_msa = {}
            for window, alignment in msaSet.items():
                filtered = _filter_alignment_gaps(alignment, threshold)
                filtered_msa[window] = filtered
            msaSet = filtered_msa

        results_ctrl.update_result(
            {"_id": result_id, "msaSet": msaSet, "status": status}
        )

        return msaSet
    except Exception as e:
        print("[Error in create_alignement]:", e)
        results_ctrl.update_result(
            {
                "_id": result_id,
                "status": "error",
            }
        )
        raise Exception("Error creating the alignement")


def create_genetic_trees(result_id, msaSet, status="genetic_trees"):
    """

    Args:
        result_id (str): the id of the result
        msaSet: the alignement
        # bootstrap_amount: the amount of bootstraps
        status (str, optional): The status of the result. Defaults to 'genetic_trees'.
    Returns:
        genetic_trees: a dictionary with the genetic trees
    """
    try:
        # Workaround for aphylogeo Linux/macOS path bug:
        # createTmpFasta()/fasttree() use cwd-relative "aphylogeo/bin/tmp".
        # Upstream fix should resolve temp paths from the package location
        # (e.g., Path(__file__).resolve().parent / "bin" / "tmp") and
        # ensure that directory exists before write/read/cleanup.
        os.makedirs(os.path.join("aphylogeo", "bin", "tmp"), exist_ok=True)
        genetic_trees = _get_aphylogeo_utils().geneticPipeline(msaSet)
        results_ctrl.update_result(
            {"_id": result_id, "genetic_trees": genetic_trees, "status": status}
        )
        return genetic_trees
    except Exception as e:
        print("[Error in create_genetic_trees]:", e)
        results_ctrl.update_result(
            {
                "_id": result_id,
                "status": "error",
            }
        )
        raise Exception("Error creating the genetic trees")


def create_output(result_id, climatic_trees, genetic_trees, climatic_df):
    """
    Creates the final output with comparison data and statistical test results.

    The output starts with the comparison data rows. The statistical test
    results are appended at the end of the DataFrame as separate rows (an
    empty separator row, followed by a header row and a values row). Only
    columns for the selected tests are included:
    - statistical_test '0' (both): Mantel_r, Mantel_p, Procrustes_M2, PROTEST_p
    - statistical_test '1' (Mantel only): Mantel_r, Mantel_p
    - statistical_test '2' (Procrustes only): Procrustes_M2, PROTEST_p
    - statistical_test '3' (none): no statistical rows are appended

    Args:
        result_id (str): the id of the result
        climatic_trees: a dictionary with the climatic trees
        genetic_trees: a dictionary with the genetic trees
        climatic_df: the climatic dataframe
    """

    try:
        aphylogeo_utils = _get_aphylogeo_utils()

        # Pre-flight: validate that genetic tree leaf names match climatic
        # specimen IDs.  A mismatch causes a cryptic ValueError inside
        # leastSquare() when find_any() returns None.
        if genetic_trees:
            first_tree = next(iter(genetic_trees.values()))
            genetic_leaf_names = {
                t.name for t in first_tree.get_terminals() if t.name
            }
            climatic_ids = set(climatic_df.iloc[:, 0].astype(str).tolist())
            missing = genetic_leaf_names - climatic_ids
            if missing:
                sample = sorted(missing)[:5]
                sample_str = ", ".join(sample) + (" …" if len(missing) > 5 else "")
                print(
                    f"[Specimen ID mismatch] {len(missing)} genetic leaf/leaves not in "
                    f"climatic data (climatic total: {len(climatic_ids)}). "
                    f"Sample: [{sample_str}]"
                )
                raise ValueError("SPECIMEN_ID_MISMATCH")

        output_list = aphylogeo_utils.filterResults(
            climatic_trees, genetic_trees, climatic_df, create_file=False
        )
        none_count = sum(1 for row in output_list if row is None)
        if none_count:
            print(f"[Warning create_output] {none_count} / {len(output_list)} rows from "
                  f"filterResults were None (specimen ID mismatch) — skipping them.")
        output_list = [row for row in output_list if row is not None]
        output = aphylogeo_utils.format_to_csv(output_list)
        df_output = pd.DataFrame(output)

        # Clean Gene column: truncate file paths to basename
        if "Gene" in df_output.columns:
            df_output["Gene"] = df_output["Gene"].apply(
                lambda x: os.path.basename(str(x)) if pd.notna(x) else x
            )

        # Run statistical tests (skip entirely when "None" is selected)
        if Params.statistical_test != '3':
            try:
                climatic_matrix = climatic_df.drop(columns=[climatic_df.columns[0]])
                climatic_dist = squareform(pdist(climatic_matrix, metric="euclidean"))
                genetic_dist = aphylogeo_utils.get_patristic_distance_matrix(genetic_trees)
                genetic_matrix = pd.DataFrame(genetic_dist)

                mantel_r = None
                mantel_p = None
                procrustes_m2 = None
                protest_p = None

                if Params.statistical_test == '0' or Params.statistical_test == '1':
                    r, p, n = aphylogeo_utils.run_mantel_test(
                        genetic_dist, climatic_dist,
                        Params.permutations_mantel_test,
                        Params.mantel_test_method
                    )
                    mantel_r = r
                    mantel_p = p

                if Params.statistical_test == '0' or Params.statistical_test == '2':
                    m2, _, _ = aphylogeo_utils.run_procrustes_analysis(genetic_matrix, climatic_matrix)
                    _, protest_p = aphylogeo_utils.run_protest_test(
                        climatic_matrix, genetic_matrix,
                        n_permutations=Params.permutations_protest
                    )
                    procrustes_m2 = m2

                # Build headers/values only for the tests that were actually run
                headers = []
                values = []
                if Params.statistical_test in ('0', '1'):
                    headers += ["Mantel_r", "Mantel_p"]
                    values += [mantel_r, mantel_p]
                if Params.statistical_test in ('0', '2'):
                    headers += ["Procrustes_M2", "PROTEST_p"]
                    values += [procrustes_m2, protest_p]

                if headers:
                    # Append empty separator row
                    empty_row = pd.DataFrame([{col: "" for col in df_output.columns}])
                    df_output = pd.concat([df_output, empty_row], ignore_index=True)

                    # Append stats header row
                    header_row_data = {col: "" for col in df_output.columns}
                    for i, header in enumerate(headers):
                        if i < len(df_output.columns):
                            header_row_data[df_output.columns[i]] = header
                    df_output = pd.concat([df_output, pd.DataFrame([header_row_data])], ignore_index=True)

                    # Append stats value row
                    value_row_data = {col: "" for col in df_output.columns}
                    for i, val in enumerate(values):
                        if i < len(df_output.columns):
                            value_row_data[df_output.columns[i]] = val
                    df_output = pd.concat([df_output, pd.DataFrame([value_row_data])], ignore_index=True)

            except Exception as e:
                print(f"[Warning] Could not compute statistical tests: {e}")

        # Convert back to dict format for storage
        # Replace NaN with None (or empty string) because MongoDB can be picky or frontend might expect it
        df_output = df_output.where(pd.notnull(df_output), None)
        output = df_output.to_dict(orient="list")

        results_ctrl.update_result(
            {"_id": result_id, "output": output, "status": "complete"}
        )
    except Exception as e:
        print("[Error in create_output]:", e)
        results_ctrl.update_result(
            {
                "_id": result_id,
                "status": "error",
            }
        )
        raise Exception(f"Error creating the output: {e}") from e


def run_genetic_pipeline(result_id, climatic_data, genetic_data, climatic_trees):
    """
    Runs the genetic pipeline from aPhyloGeo.
    Args:
        result_id: string with the id of the database result
        climatic_data: json object with the climatic data
        genetic_data: json object with the genetic data
        # genetic_params: json object with the genetic parameters
        # genetic_file_name: string with the name of the genetic file
        # genetic_files_id: string with the id of the genetic file
        climatic_trees: dict of the climatic trees
    returns:
        result_id: string with the id of the database result
    """

    msaSet = create_alignement(result_id, genetic_data)

    genetic_trees = create_genetic_trees(result_id, msaSet)

    create_output(
        result_id,
        climatic_trees,
        genetic_trees,
        pd.read_json(io.StringIO(climatic_data)),
    )

    return result_id


def make_cookie(
    result_id, auth_cookie, response, name=COOKIE_NAME, max_age=COOKIE_MAX_AGE
):
    """
    Create a cookie with the result id

    Args:
        result_id (str): The id of the result to add to the cookie
        auth_cookie (str): The current cookie value
        response (Response): The response object to set the cookie on
        name (str, optional): The name of the cookie. Defaults to COOKIE_NAME.
        max_age (int, optional): The max age of the cookie. Defaults to COOKIE_MAX_AGE.

    """
    # If the "Auth" cookie exists, split the value into a list of IDs
    auth_ids = [] if not auth_cookie else auth_cookie.split(".")
    if result_id not in auth_ids and result_id != "":
        auth_ids.append(result_id)

    # Create the string format for the cookie
    auth_cookie_value = ".".join(auth_ids)
    response.set_cookie(name, auth_cookie_value, max_age=max_age)


def get_table_styles():
    """
    Returns the common styles for the dash tables.
    """
    return {
        "style_table": {
            "overflowX": "auto",
        },
        "style_header": {
            "fontWeight": "600",
            "textTransform": "uppercase",
            "fontSize": "13px",
            "textAlign": "center",
            "color": "#ffffff",
            "border": "none",
        },
        "style_data": {
            "color": "var(--reverse-black-white-color)",
            "backgroundColor": "var(--table-bg-color)",
            "fontSize": "13px",
        },
        "style_filter": {
            "backgroundColor": "var(--table-alt-row-color, #f8f9fa)",
            "padding": "8px",
            "borderBottom": "1px solid var(--table-border-color, rgba(0,0,0,0.1))",
            "borderRight": "1px solid var(--table-border-color, rgba(0,0,0,0.1))",
            "borderLeft": "none",
            "borderTop": "none",
        },
        "style_data_conditional": [
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "var(--table-alt-row-color)",
            },
            {
                "if": {"state": "active"},
                "backgroundColor": "rgba(102, 126, 234, 0.15)",
                "border": "none",
            },
        ],
        "style_cell": {
            "textAlign": "left",
            "padding": "12px",
            "fontFamily": "Inter, sans-serif",
        },
        "css": [
            {
                "selector": ".dash-spreadsheet tr:hover",
                "rule": "background-color: transparent !important;",
            },
            {
                "selector": ".dash-spreadsheet tr:first-child th",
                "rule": "background-color: var(--action) !important;",
            },
            {
                "selector": ".dash-spreadsheet tr:nth-child(2) th:hover",
                "rule": "background-color: var(--table-alt-row-color, #f8f9fa) !important;",
            },
            {
                "selector": "tr:first-child .dash-select-header",
                "rule": "background-color: var(--action) !important; border: none !important;",
            },
        ],
    }
