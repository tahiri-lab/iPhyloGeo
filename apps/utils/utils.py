import pandas as pd
import base64
import io
import os
from Bio import SeqIO
from dash import dcc, html

import db.controllers.files as files_ctrl
import db.controllers.results as results_ctrl
from aPhyloGeo import aPhyloGeo

FILES_PATH = 'files/'
COOKIE_NAME = 'AUTH'
COOKIE_MAX_AGE = 8640000  # 100 days

# TODO add this to the .env file
APP_ENV = 'local'  # os.environ.get('APP_ENV', 'local')


def get_all_files():
    return files_ctrl.get_all_files()


def get_results(ids):
    return results_ctrl.get_results(ids)


def get_result(id):
    return results_ctrl.get_result(id)


def get_all_results():
    return results_ctrl.get_all_results()


def get_file(id, options={}):
    """
        Get the file with the given id.
        If the app is running in local mode, the file is read from the local file system.
        Otherwise, the file is read from database.
    """
    # for testing purposes
    if 'mongo' in options and options['mongo']:
        return get_file_from_db(id)

    if APP_ENV == 'local':
        return read_local_file(FILES_PATH + id, options)
    else:
        return get_file_from_db(id)


def read_local_file(path, options={}):
    """ Read the file from the local file system.

    Args:
        path (string): The path of the file.
    """
    # check if the file exists
    if not os.path.isfile(path):
        return None
    # read the file
    if 'pd' in options:
        return pd.read_csv(path)


def get_file_from_db(id):
    """ Get the file from the database.

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
    for content, file_name, date in zip(list_of_contents, list_of_names, last_modifieds):
        results.append(parse_contents(content, file_name, date))

    return results


def save_files(results):
    return files_ctrl.save_files(results)


def download_file_from_db(id, root_path='./'):
    """ Download the file from the database.

    Args:
        id (string): The id of the file.
    """
    res = get_file(id, {"mongo": True})

    with open(root_path + res['file_name'], 'wb') as f:
        if res['file_name'].endswith('.xlsx'):
            res['df'].to_excel(f, index=False, header=True)
        elif res['file_name'].endswith('.csv'):
            res['df'].to_csv(f, index=False, header=True)
        elif res['file_name'].endswith('.fasta'):
            res['file'] = SeqIO.to_dict(res['file'])
            fasta_str = ''
            for key, seq in res['file'].items():
                fasta_str += f'>{key}\n{str(seq.seq)}\n'
            f.write(fasta_str.encode('utf-8'))


def parse_contents(content, file_name, date):
    res = {
        'file_name': file_name,
        'last_modified_date': date,
    }

    try:
        content_type, content_string = content.split(',')
        decoded_content = base64.b64decode(content_string)

        if content_type == 'data:text/csv;base64' or content_type == 'data:application/vnd.ms-excel;base64':
            # Assume that the user uploaded a CSV file
            res['df'] = pd.read_csv(io.StringIO(decoded_content.decode('utf-8')))
            res['type'] = 'climatic'
        elif 'xls' in file_name:
            # Assume that the user uploaded an excel file
            res['df'] = pd.read_excel(io.BytesIO(decoded_content))
            res['type'] = 'climatic'
        elif 'fasta' in file_name:
            # res['file'] = SeqIO.parse(io.StringIO(decoded_content.decode('utf-8')), 'fasta')
            res['file'] = files_ctrl.fasta_to_str(SeqIO.parse(io.StringIO(decoded_content.decode('utf-8')), 'fasta'))
            res['type'] = 'genetic'
        else:
            res['error'] = True

        return res
    except Exception as e:
        print(e)


def create_seq_html(file):
    file_name = file['file_name']

    if 'error' in file and file['error']:
        return html.Div([
            dcc.Markdown('Please upload a **fasta file**.'),
        ])

    return html.Div([
        dcc.Markdown('You have uploades file(s):  **{}**'.format(file_name)),
    ])


def create_result(files_ids, result_type, climatic_params=None, genetic_params=None, name='result', status='pending'):
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
        result = {
            'name': name,
            'status': status,
            'result_type': result_type
        }

        if 'climatic_files_id' in files_ids:
            result['climatic_files_id'] = files_ids['climatic_files_id']
        if 'genetic_files_id' in files_ids:
            result['genetic_files_id'] = files_ids['genetic_files_id']
        if genetic_params and 'genetic' in result_type:
            result['genetic_params'] = genetic_params
        if climatic_params and 'climatic' in result_type:
            result['climatic_params'] = climatic_params

        return results_ctrl.create_result(result)

    except Exception as e:
        print('[Error]:', e)
        raise Exception('Error creating the result')


def create_climatic_trees(result_id, climatic_data, climatic_params, status='climatic_trees'):
    """ Creates a climatic result.

    Args:
        climatic_data: json object with the climatic data
        climatic_params: json object with the climatic parameters
        status (str, optional): The status of the result. Defaults to 'climatic_trees'.

    Returns:
        climatic_trees: a dictionary with the climatic trees
        result_id: the id of the created result
    """
    try:
        df = pd.read_json(climatic_data)
        names = ['id'] + climatic_params['names']
        climatic_trees = aPhyloGeo.climaticPipeline(df, names)
        results_ctrl.update_result({
            '_id': result_id,
            'climatic_trees': climatic_trees,
            'status': status,
        })
        return climatic_trees
    except Exception as e:
        print('[Error]:', e)
        results_ctrl.update_result({
            '_id': result_id,
            'status': 'error',
        })
        raise Exception('Error creating the climatic trees')


def create_alignement(result_id, genetic_data, window_size, step_size, bootstrap_amount, status='alignement'):
    """
    Creates the alignement of the genetic data.

    Args:
        result_id (str): the id of the result
        genetic_data: json object with the genetic data
        window_size: the size of the window
        step_size: the size of the step
        bootstrap_amount: the amount of bootstraps

    Returns:
        msaSet: the alignement
    """
    try:

        alignementObject = aPhyloGeo.AlignSequences(genetic_data, window_size, step_size, False, bootstrap_amount)
        msaSet = alignementObject.msaSet

        results_ctrl.update_result({
            '_id': result_id,
            'msaSet': msaSet,
            'status': status
        })

        return msaSet
    except Exception as e:
        print('[Error]:', e)
        results_ctrl.update_result({
            '_id': result_id,
            'status': 'error',
        })
        raise Exception('Error creating the alignement')


def create_genetic_trees(result_id, msaSet, bootstrap_amount, status='genetic_trees'):
    """

    Args:
        result_id (str): the id of the result
        msaSet: the alignement
        bootstrap_amount: the amount of bootstraps
        status (str, optional): The status of the result. Defaults to 'genetic_trees'.
    Returns:
        genetic_trees: a dictionary with the genetic trees
    """
    try:
        genetic_trees = aPhyloGeo.createBoostrap(msaSet, bootstrap_amount)
        results_ctrl.update_result({
            '_id': result_id,
            'genetic_trees': genetic_trees,
            'status': status
        })
        return genetic_trees
    except Exception as e:
        print('[Error]:', e)
        results_ctrl.update_result({
            '_id': result_id,
            'status': 'error',
        })
        raise Exception('Error creating the genetic trees')


def create_output(result_id, climatic_trees, genetic_trees, bootstrap_threshold, ls_threshold, climatic_df, genetic_file_name):
    """

    Args:
        result_id (str): the id of the result
        climatic_trees: a dictionary with the climatic trees
        genetic_trees: a dictionary with the genetic trees
        bootstrap_threshold: the bootstrap threshold
        ls_threshold: the ls threshold
        climatic_df: the climatic dataframe
        genetic_file_name: the name of the genetic file

    """
    try:
        output = aPhyloGeo.filterResults(climatic_trees, genetic_trees, bootstrap_threshold, ls_threshold, climatic_df, genetic_file_name)
        results_ctrl.update_result({
            '_id': result_id,
            'output': output,
            'status': 'complete'
        })
    except Exception as e:
        print('[Error]:', e)
        results_ctrl.update_result({
            '_id': result_id,
            'status': 'error',
        })
        raise Exception('Error creating the output')


def run_genetic_pipeline(result_id, climatic_data, genetic_data, genetic_params, genetic_file_name, climatic_trees):
    """
    Runs the genetic pipeline from aPhyloGeo.
    Args:
        climatic_data: json object with the climatic data
        genetic_data: json object with the genetic data
        genetic_params: json object with the genetic parameters
        genetic_file_name: string with the name of the genetic file
        genetic_files_id: string with the id of the genetic file
        climatic_trees: dict of the climatic trees
        result_id: string with the id of the database result
    returns:
        result_id: string with the id of the database result
    """

    msaSet = create_alignement(result_id, genetic_data, genetic_params['window_size'], genetic_params['step_size'], genetic_params['bootstrap_amount'])

    genetic_trees = create_genetic_trees(result_id, msaSet, genetic_params['bootstrap_amount'])

    create_output(result_id, climatic_trees, genetic_trees, genetic_params['bootstrap_threshold'], genetic_params['ls_threshold'], pd.read_json(climatic_data), genetic_file_name)

    return result_id


def make_cookie(result_id, auth_cookie, response, name=COOKIE_NAME, max_age=COOKIE_MAX_AGE):
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
    auth_ids = [] if not auth_cookie else auth_cookie.split('.')
    if result_id not in auth_ids and result_id != '':
        auth_ids.append(result_id)

    # Create the string format for the cookie
    auth_cookie_value = '.'.join(auth_ids)
    response.set_cookie(name, auth_cookie_value, max_age=max_age)
