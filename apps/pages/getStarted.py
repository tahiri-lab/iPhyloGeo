import base64
import io
import json
import re

import dash
import db.controllers.files as files_ctrl
import db.controllers.results as results_ctrl
from components.badge import create_badge
from components.email_input import (
    get_button_id,
    validate_email,
)
from enums import convert_settings_to_codes
import pages.upload.climatic.paramsClimatic as paramsClimatic
import pages.upload.dropFileSection as dropFileSection
import pages.upload.genetic.paramsGenetic as paramsGenetic
import pages.upload.submitButton as submitButton
import pages.utils.popup as popup
import pages.utils.result_ready_popup as result_ready_popup
import pandas as pd
import utils.mail as mail
import utils.utils as utils
import utils.background_tasks as background_tasks
from utils.i18n import LANGUAGE_LIST, t
from utils.time import format_remaining_time
from aphylogeo.params import Params
from Bio import AlignIO, SeqIO
from dash import Input, Output, State, callback, ctx, dcc, html
from dash.exceptions import PreventUpdate
from flask import request

_SETTINGS_FILE_PATH = "genetic_settings_file.json"

# Load genetic settings from genetic settings file (JSON)
with open(_SETTINGS_FILE_PATH, "r", encoding="utf-8") as genetic_settings_fp:
    genetic_setting_file = json.load(genetic_settings_fp)


def _read_genetic_settings() -> dict:
    try:
        with open(_SETTINGS_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return genetic_setting_file


# Update Params for aPhyloGeo (convert readable names to codes)
# Filter to only keys recognized by aphylogeo's Params to avoid ValueError
_converted = convert_settings_to_codes(genetic_setting_file)
Params.update_from_dict({k: v for k, v in _converted.items() if k in Params.PARAMETER_KEYS})

CONTENT_CLIMATIC = "data:text/csv;base64,aWQsQUxMU0tZX1NGQ19TV19EV04sVDJNLFFWMk0sUFJFQ1RPVENPUlIsV1MxME0NCk9NNzM5MDUzLDQuNywxNC44MDMzMzMzMzMzMzMzMzUsNi43MTMzMzMzMzMzMzMzMzQsMS42MjMzMzMzMzMzMzMzMzMsMi41NTMzMzMzMzMzMzMzMzMyDQpPVTQ3MTA0MCwxLjQ2LDQuMTksNC41MTY2NjY2NjY2NjY2NjcsMC4xMiwzLjA0MzMzMzMzMzMzMzMzMw0KT04xMjk0MjksNi44OTMzMzMzMzMzMzMzMzM1LDI3LjA2NjY2NjY2NjY2NjY2NiwxNS4xNTY2NjY2NjY2NjY2NjUsMC43MTY2NjY2NjY2NjY2NjY3LDEuMzYNCk9MOTg5MDc0LDQuNjQ2NjY2NjY2NjY2NjY2NSwyNi4xMiwxOC4xMDY2NjY2NjY2NjY2NzYsMC40NzMzMzMzMzMzMzMzMzM0LDUuNjYNCk9OMTM0ODUyLDYuODQwMDAwMDAwMDAwMDAyNSwxNi45NzMzMzMzMzMzMzMzMzMsNS41NzY2NjY2NjY2NjY2NjcsMC40OTY2NjY2NjY2NjY2NjY2LDQuNjY2NjY2NjY2NjY2NjY3"
CONTENT_GENETIC = "data:application/octet-stream;base64,Pk9OMTI5NDI5DQpBQ1RUVENHQVRDVENUVEdUQUdBVENUR1RUQ1RDVEFBQUNHQUFDVFRUQUFBQVRDVEdUR1RHR0NUR1RDQUMNClRDR0dDVEdDQVRHQ1RUQUdUR0NBQ1RDQUNHQ0FHVEFUQUFUVEFBVEFBQ1RBQVRUQUNUR1RDR1RUR0FDQQ0KR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQ1RUQ1RHQ0FHR0NUR0NUVEFDR0dUVFRDR1RDQ0dUR1RUR0NBR0NDDQpHQVRDQVRDQUdDQUNBVENUQUdHVFRUVEdUQ0NHR0dUR1RHQUNDR0FBQUdHVEFBR0FUR0dBR0FHQ0NUVEcNClRDQ0NUR0dUVFRDQUFDR0FHQUFBQUNBQ0FDR1RDQ0FBQ1RDQUdUVFRHQ0NUR1RUVFRBQ0FHR1RUQ0dDRw0KQUNHVEdDVENHVEFDR1RHR0NUVFRHR0FHQUNUQ0NHVEdHQUdHQUdHVENUVEFUQ0FHQUdHQ0FDR1RDQUFDDQpBVENUVEFBQUdBVEdHQ0FDVFRHVEdHQ1RUQUdUQUdBQUdUVEdBQUFBQUdHQ0dUVFRUR0NDVENBQUNUVEcNCkFBQ0FHQ0NDVEFUR1RHVFRDQVRDQUFBQ0dUVENHR0FUR0NUQ0dBQUNUR0NBQ0NUQ0FUR0dUQ0FUR1RUQQ0KVEdHVFRHQVRDVEdHVEFHQ0FHQUFDVENHQUFHR0NBVFRDQUdUQUNHR1RDR1RBR1RHR1RHQUdBQ0FDVFRHDQpHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHQ0dBQUFUQUNDQUdUR0dDVFRBQ0NHQ0FBR0dUVENUVENUVENHVEENCkFHQUFDR0dUQUFUQUFBR0dBR0NUR0dUR0dDQ0FUQUdUVEFDR0dDR0NDR0FUQ1RBQUFHVENBVFRUR0FDVA0KVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQVRDQ1RUQVRHQUFHQVRUVFRDQUFHQUFBQUNUR0dBQUNBQ1RBQUFDDQpBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBQUNUQ0FUR0NHVEdBR0NUVEFBQ0dHQUdHR0dDQVRBQ0FDVENHQ1QNCkFUR1RDR0FUQUFDQUFDVFRDVEdUR0dDQ0NUR0FUR0dDVEFDQ0NUQ1RUR0FHVEdDQVRUQUFBR0FDQ1RUQw0KVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQ0FUR0NBQ1RUVEdUQ1RHQUFDQUFDVEdHQUNUVFRBVFRHQUNBQ1RBDQpBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHVEdBQUNBVEdBR0NBVEdBQUFUVEdDVFRHR1RBQ0FDR0dBQUNHVFQNCkNUR0FBQUFHQUdDVEFUR0FBVFRHQ0FHQUNBQ0NUVFRUR0FBQVRUQUFBVFRHR0NBQUFHQUFBVFRUR0FDQQ0KQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQVRUVFRHVEFUVFRDQ0NUVEFBQVRUQ0NBVEFBVENBQUdBQ1RBVFRDDQpBQUNDQUFHR0dUVEdBQUFBR0FBQUFBR0NUVEdBVEdHQ1RUVEFUR0dHVEFHQUFUVENHQVRDVEdUQ1RBVEMNCkNBR1RUR0NHVENBQ0NBQUFUR0FBVEdDQUFDQ0FBQVRHVEdDQ1RUVENBQUNUQ1RDQVRHQUFHVEdUR0FUQw0KQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQUdBQ0dHR0NHQVRUVFRHVFRBQUFHQ0NBQ1RUR0NHQUFUVFRUR1RHDQo+T04xMzQ4NTINCkFHQVRDVEdUVENUQ1RBQUFDR0FBQ1RUVEFBQUFUQ1RHVEdUR0dDVEdUQ0FDVENHR0NUR0NBVEdDVFRBRw0KVEdDQUNUQ0FDR0NBR1RBVEFBVFRBQVRBQUNUQUFUVEFDVEdUQ0dUVEdBQ0FHR0FDQUNHQUdUQUFDVENHDQpUQ1RBVENUVENUR0NBR0dDVEdDVFRBQ0dHVFRUQ0dUQ0NHVEdUVEdDQUdDQ0dBVENBVENBR0NBQ0FUQ1QNCkFHR1RUVFRHVENDR0dHVEdUR0FDQ0dBQUFHR1RBQUdBVEdHQUdBR0NDVFRHVENDQ1RHR1RUVENBQUNHQQ0KR0FBQUFDQUNBQ0dUQ0NBQUNUQ0FHVFRUR0NDVEdUVFRUQUNBR0dUVENHQ0dBQ0dUR0NUQ0dUQUNHVEdHDQpDVFRUR0dBR0FDVENDR1RHR0FHR0FHR1RDVFRBVENBR0FHR0NBQ0dUQ0FBQ0FUQ1RUQUFBR0FUR0dDQUMNClRUR1RHR0NUVEFHVEFHQUFHVFRHQUFBQUFHR0NHVFRUVEdDQ1RDQUFDVFRHQUFDQUdDQ0NUQVRHVEdUVA0KQ0FUQ0FBQUNHVFRDR0dBVEdDVENHQUFDVEdDQUNDVENBVEdHVENBVEdUVEFUR0dUVEdBR0NUR0dUQUdDDQpBR0FBQ1RDR0FBR0dDQVRUQ0FHVEFDR0dUQ0dUQUdUR0dUR0FHQUNBQ1RUR0dUR1RDQ1RUR1RDQ0NUQ0ENClRHVEdHR0NHQUFBVEFDQ0FHVEdHQ1RUQUNDR0NBQUdHVFRDVFRDVFRDR1RBQUdBQUNHR1RBQVRBQUFHRw0KQUdDVEdHVEdHQ0NBVEFHVFRBQ0dHQ0dDQ0dBVENUQUFBR1RDQVRUVEdBQ1RUQUdHQ0dBQ0dBR0NUVEdHDQpDQUNUR0FUQ0NUVEFUR0FBR0FUVFRUQ0FBR0FBQUFDVEdHQUFDQUNUQUFBQ0FUQUdDQUdUR0dUR1RUQUMNCkNDR1RHQUFDVENBVEdDR1RHQUdDVFRBQUNHR0FHR0dHQ0FUQUNBQ1RDR0NUQVRHVENHQVRBQUNBQUNUVA0KQ1RHVEdHQ0NDVEdBVEdHQ1RBQ0NDVENUVEdBR1RHQ0FUVEFBQUdBQ0NUVENUQUdDQUNHVEdDVEdHVEFBDQpBR0NUVENBVEdDQUNUVFRHVENDR0FBQ0FBQ1RHR0FDVFRUQVRUR0FDQUNUQUFHQUdHR0dUR1RBVEFDVEcNCkNUR0NDR1RHQUFDQVRHQUdDQVRHQUFBVFRHQ1RUR0dUQUNBQ0dHQUFDR1RUQ1RHQUFBQUdBR0NUQVRHQQ0KQVRUR0NBR0FDQUNDVFRUVEdBQUFUVEFBQVRUR0dDQUFBR0FBQVRUVEdBQ0FDQ1RUQ0FBVEdHR0dBQVRHDQpUQ0NBQUFUVFRUR1RBVFRUQ0NDVFRBQUFUVENDQVRBQVRDQUFHQUNUQVRUQ0FBQ0NBQUdHR1RUR0FBQUENCkdBQUFBQUdDVFRHQVRHR0NUVFRBVEdHR1RBR0FBVFRDR0FUQ1RHVENUQVRDQ0FHVFRHQ0dUQ0FDQ0FBQQ0KVEdBQVRHQ0FBQ0NBQUFUR1RHQ0NUVFRDQUFDVENUQ0FUR0FBR1RHVEdBVENBVFRHVEdHVEdBQUFDVFRDDQpBVEdHQ0FHQUNHR0dDR0FUVFRUR1RUQUFBR0NDQUNUVEdDR0FBVFRUVEdUR0dDQUNUR0FHQUFUVFRHQUMNClQNCj5PTDk4OTA3NA0KQVRUQUFBR0dUVFRBVEFDQ1RUQ0NDQUdHVEFBQ0FBQUNDQUFDQ0FBQ1RUVENHQVRDVENUVEdUQUdBVENUDQpHVFRDVFRUQUFBQ0dBQUNUVFRBQUFBVENUR1RHVEdHQ1RHVENBQ1RDR0dDVEdDQVRHQ1RUQUdUR0NBQ1QNCkNBQ0dDQUdUQVRBQVRUQUFUQUFDVEFBVFRBQ1RHVENHVFRHQUNBR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQw0KVFRDVEdDQUdHQ1RHQ1RUQUNHR1RUVENHVENDR1RHVFRHQ0FHQ0NHQVRDQVRDQUdDQUNBVENUQUdHVFRUDQpUR1RDQ0dHR1RHVEdBQ0NHQUFBR0dUQUFHQVRHR0FHQUdDQ1RUR1RDQ0NUR0dUVFRDQUFDR0FHQUFBQUMNCkFDQUNHVENDQUFDVENBR1RUVEdDQ1RHVFRUVEFDQUdHVFRDR0NHQUNHVEdDVENHVEFDR1RHR0NUVFRHRw0KQUdBQ1RDQ0dUR0dBR0dBR0dUQ1RUQVRDQUdBR0dDQUNHVENBQUNBVENUVEFBQUdBVEdHQ0FDVFRHVEdHDQpDVFRBR1RBR0FBR1RUR0FBQUFBR0dDR1RUVFRHQ0NUQ0FBQ1RUR0FBQ0FHQ0NDVEFUR1RHVFRDQVRDQUENCkFDR1RUQ0dHQVRHQ1RDR0FBQ1RHQ0FDQ1RDQVRHR1RDQVRHVFRBVEdHVFRHQUdDVEdHVEFHQ0FHQUFDVA0KQ0dBQUdHQ0FUVENBR1RBQ0dHVENHVEFHVEdHVEdBR0FDQUNUVEdHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHDQpDR0FBQVRBQ0NBR1RHR0NUVEFDQ0dDQUFHR1RUQ1RUQ1RUQ0dUQUFHQUFDR0dUQUFUQUFBR0dBR0NUR0cNClRHR0NDQVRBR1RUQUNHR0NHQ0NHQVRDVEFOTk5OTk5OTk5HQUNUVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQQ0KVENDVFRBVEdBQUdBVFRUVENBQUdBQUFBQ1RHR0FBQ0FDVEFBQUNBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBDQpBQ1RDQVRHQ0dUR0FHQ1RUQUFDR0dBR0dHR0NBVEFDQUNUQ0dDVEFUR1RDR0FUQUFDQUFDVFRDVEdUR0cNCkNDQ1RHQVRHR0NUQUNDQ1RDVFRHQUdUR0NBVFRBQUFHQUNDVFRDVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQw0KQVRHQ0FDVFRUR1RDQ0dBQUNBQUNUR0dBQ1RUVEFUVEdBQ0FDVEFBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHDQpUR0FBQ0FUR0FHQ0FUR0FBQVRUR0NUVEdHVEFDQUNHR0FBQ0dUVENUR0FBQUFHQUdDVEFUR0FBVFRHQ0ENCkdBQ0FDQ1RUVFRHQUFBVFRBQUFUVEdHQ0FBQUdBQUFUVFRHQUNBQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQQ0KVFRUVEdUQVRUVENDQ1RUQUFBVFRDQ0FUQUFUQ0FBR0FDVEFUVENBQUNDQUFHR0dUVEdBQUFBR0FBQUFBDQpHQ1RUR0FUR0dDVFRUQVRHR0dUQUdBQVRUQ0dBVENUR1RDVEFUQ0NBR1RUR0NHVENBQ0NBQUFUR0FBVEcNCkNBQUNDQUFBVEdUR0NDVFRUQ0FBQ1RDVENBVEdBQUdUR1RHQVRDQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQQ0KPk9NNzM5MDUzDQpBQ1RUVENHQVRDVENUVEdUQUdBVENUR1RUQ1RDVEFBQUNHQUFDVFRUQUFBQVRDVEdUR1RHR0NUR1RDQUMNClRDR0dDVEdDQVRHQ1RUQUdUR0NBQ1RDQUNHQ0FHVEFUQUFUVEFBVEFBQ1RBQVRUQUNUR1RDR1RUR0FDQQ0KR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQ1RUQ1RHQ0FHR0NUR0NUVEFDR0dUVFRDR1RDQ0dUR1RUR0NBR0NDDQpHQVRDQVRDQUdDQUNBVENUQUdHVFRUVEdUQ0NHR0dUR1RHQUNDR0FBQUdHVEFBR0FUR0dBR0FHQ0NUVEcNClRDQ0NUR0dUVFRDQUFDR0FHQUFBQUNBQ0FDR1RDQ0FBQ1RDQUdUVFRHQ0NUR1RUVFRBQ0FHR1RUQ0dDRw0KQUNHVEdDVENHVEFDR1RHR0NUVFRHR0FHQUNUQ0NHVEdHQUdHQUdHVENUVEFUQ0FHQUdHQ0FDR1RDQUFDDQpBVENUVEFBQUdBVEdHQ0FDVFRHVEdHQ1RUQUdUQUdBQUdUVEdBQUFBQUdHQ0dUVFRUR0NDVENBQUNUVEcNCkFBQ0FHQ0NDVEFUR1RHVFRDQVRDQUFBQ0dUVENHR0FUR0NUQ0dBQUNUR0NBQ0NUQ0FUR0dUQ0FUR1RUQQ0KVEdHVFRHQVRDVEdHVEFHQ0FHQUFDVENHQUFHR0NBVFRDQUdUQUNHR1RDR1RBR1RHR1RHQUdBQ0FDVFRHDQpHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHQ0dBQUFUQUNDQUdUR0dDVFRBQ0NHQ0FBR0dUVENUVENUVENHVEENCkFHQUFDR0dUQUFUQUFBR0dBR0NUR0dUR0dDQ0FUQUdUVEFDR0dDR0NDR0FUQ1RBQUFHVENBVFRUR0FDVA0KVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQVRDQ1RUQVRHQUFHQVRUVFRDQUFHQUFBQUNUR0dBQUNBQ1RBQUFDDQpBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBQUNUQ0FUR0NHVEdBR0NUVEFBQ0dHQUdHR0dDQVRBQ0FDVENHQ1QNCkFUR1RDR0FUQUFDQUFDVFRDVEdUR0dDQ0NUR0FUR0dDVEFDQ0NUQ1RUR0FHVEdDQVRUQUFBR0FDQ1RUQw0KVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQ0FUR0NBQ1RUVEdUQ1RHQUFDQUFDVEdHQUNUVFRBVFRHQUNBQ1RBDQpBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHVEdBQUNBVEdBR0NBVEdBQUFUVEdDVFRHR1RBQ0FDR0dBQUNHVFQNCkNUR0FBQUFHQUdDVEFUR0FBVFRHQ0FHQUNBQ0NUVFRUR0FBQVRUQUFBVFRHR0NBQUFHQUFBVFRUR0FDQQ0KQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQVRUVFRHVEFUVFRDQ0NUVEFBQVRUQ0NBVEFBVENBQUdBQ1RBVFRDDQpBQUNDQUFHR0dUVEdBQUFBR0FBQUFBR0NUVEdBVEdHQ1RUVEFUR0dHVEFHQUFUVENHQVRDVEdUQ1RBVEMNCkNBR1RUR0NHVENBQ0NBQUFUR0FBVEdDQUFDQ0FBQVRHVEdDQ1RUVENBQUNUQ1RDQVRHQUFHVEdUR0FUQw0KQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQUdBQ0dHR0NHQVRUVFRHVFRBQUFHQ0NBQ1RUR0NHQUFUVFRUR1RHDQo+T1U0NzEwNDANCkFBQ0FBQUNDQUFDQ0FBQ1RUVENHQVRDVENUVEdUQUdBVENUR1RUQ1RDVEFBQUNHQUFDVFRUQUFBQVRDVA0KR1RHVEdHQ1RHVENBQ1RDR0dDVEdDQVRHQ1RUQUdUR0NBQ1RDQUNHQ0FHVEFUQUFUVEFBVEFBQ1RBQVRUDQpBQ1RHVENHVFRHQUNBR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQ1RUQ1RHQ0FHR0NUR0NUVEFDR0dUVFRDR1QNCkNDR1RHVFRHQ0FHQ0NHQVRDQVRDQUdDQUNBVENUQUdHVFRUVEdUQ0NHR0dUR1RHQUNDR0FBQUdHVEFBRw0KQVRHR0FHQUdDQ1RUR1RDQ0NUR0dUVFRDQUFDR0FHQUFBQUNBQ0FDR1RDQ0FBQ1RDQUdUVFRHQ0NUR1RUDQpUVEFDQUdHVFRDR0NHQUNHVEdDVENHVEFDR1RHR0NUVFRHR0FHQUNUQ0NHVEdHQUdHQUdHVENUVEFUQ0ENCkdBR0dDQUNHVENBQUNBVENUVEFBQUdBVEdHQ0FDVFRHVEdHQ1RUQUdUQUdBQUdUVEdBQUFBQUdHQ0dUVA0KVFRHQ0NUQ0FBQ1RUR0FBQ0FHQ0NDVEFUR1RHVFRDQVRDQUFBQ0dUVENHR0FUR0NUQ0dBQUNUR0NBQ0NUDQpDQVRHR1RDQVRHVFRBVEdHVFRHQUdDVEdHVEFHQ0FHQUFDVENHQUFHR0NBVFRDQUdUQUNHR1RDR1RBR1QNCkdHVEdBR0FDQUNUVEdHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHQ0dBQUFUQUNDQUdUR0dDVFRBQ0NHQ0FBRw0KR1RUQ1RUQ1RUQ0dUQUFHQUFDR0dUQUFUQUFBR0dBR0NUR0dUR0dDQ0FUQUdUVEFDR0dDR0NDR0FUQ1RBDQpBQUdUQ0FUVFRHQUNUVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQVRDQ1RUQVRHQUFHQVRUVFRDQUFHQUFBQUMNClRHR0FBQ0FDVEFBQUNBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBQUNUQ0FUR0NHVEdBR0NUVEFBQ0dHQUdHRw0KR0NBVEFDQUNUQ0dDVEFUR1RDR0FUQUFDQUFDVFRDVEdUR0dDQ0NUR0FUR0dDVEFDQ0NUQ1RUR0FHVEdDDQpBVFRBQUFHQUNDVFRDVEFHQ0FDR1RHQ1RHR1RBQUFHQ0NBQ1RUR0NHQUFUVFRUR1RHDQpUVEFUVEdBQ0FDVEFBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHVEdBQUNBVEdBR0NBVEdBQUFUVEdDVFRHRw0KVEFDQUNHR0FBQ0dUVENUR0FBQUFHQUdDVEFUR0FBVFRHQ0FHQUNBQ0NUVFRUR0FBQVRUQUFBVFRHR0NBDQpBQUdBQUFUVFRHQUNBQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQVRUVFRHVEFUVFRDQ0NUVEFBQVRUQ0NBVEENCkFUQ0FBR0FDVEFUVENBQUNDQUFHR0dUVEdBQUFBR0FBQUFBR0NUVEdBVEdHQ1RUVEFUR0dHVEFHQUFUVA0KQ0dBVENUR1RDVEFUQ0NBR1RUR0NHVENBQ0NBQUFUR0FBVEdDQUFDQ0FBQVRHVEdDQ1RUVENBQUNUQ1RDDQpBVEdBQUdUR1RHQVRDQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQUdBQ0dHR0NHQVRUVFRHVFRBQUFHQ0NBQ1Q="

dash.register_page(__name__, path="/getStarted")

CSV_REGEX = re.compile(r".*\.csv")
EXCEL_REGEX = re.compile(r".*\.xls[x]?$")
FASTA_REGEX = re.compile(r".*\.fasta$")
JSON_REGEX = re.compile(r".*\.json")


def layout():
    from flask import request
    _lang = request.cookies.get("lang", "en")
    return _build_layout(_lang)


def _build_layout(lang="en"):
    settings = _read_genetic_settings()
    return html.Div(
    [
        dcc.Store(id="ready-for-pipeline", data=False),
        dcc.Store(id="pipeline-started", data=False),
        dcc.Store(id="popup-dismissed", data=False),
        dcc.Interval(
            id="pipeline-status-interval",
            interval=1000,  # Poll every 1 second
            n_intervals=0,
            disabled=True,  # Disabled by default
        ),
        dcc.Store(id="consent-choice-store", storage_type="memory", data=None),
        dcc.Store(
            id="input-data",
            data={
                "genetic": {
                    "file": None,
                    "file_name": None,
                    "last_modified_date": None,
                    "type": "genetic",
                },
                "climatic": {
                    "file": None,
                    "file_name": None,
                    "last_modified_date": None,
                    "type": "climatic",
                },
                "aligned_genetic": {
                    "file": None,
                    "file_name": None,
                    "last_modified_date": None,
                    "type": None,
                },
                "genetic_tree": {
                    "file": None,
                    "file_name": None,
                    "last_modified_date": None,
                    "type": None,
                },
                "submit button": False,
            },
        ),
        dcc.Store(id="params-climatic", data={"names": None}),
        dcc.Store(id="result-name-store", storage_type="memory", data=""),
        dcc.Store(
            id="params-genetic",
            data={
                "window_size": settings["window_size"],
                "step_size": settings["step_size"],
                "bootstrap_threshold": settings["bootstrap_threshold"],
                "dist_threshold": settings["dist_threshold"],
                "alignment_method": settings["alignment_method"],
                "distance_method": settings["distance_method"],
                "fit_method": settings["fit_method"],
                "tree_type": settings["tree_type"],
                "rate_similarity": settings["rate_similarity"],
                "method_similarity": settings["method_similarity"],
                "preprocessing_genetic": settings.get("preprocessing_genetic", "Disabled"),
                "preprocessing_climatic": settings.get("preprocessing_climatic", "Disabled"),
                "preprocessing_threshold_genetic": settings.get("preprocessing_threshold_genetic", 0),
                "preprocessing_threshold_climatic": settings.get("preprocessing_threshold_climatic", 0),
                "correlation_climatic_enabled": settings.get("correlation_climatic_enabled", "Disabled"),
                "correlation_threshold_climatic": settings.get("correlation_threshold_climatic", 1),
                "permutations_mantel_test": settings.get("permutations_mantel_test", 999),
                "permutations_protest": settings.get("permutations_protest", 999),
                "mantel_test_method": settings.get("mantel_test_method", "Pearson"),
                "statistical_test": settings.get("statistical_test", "Both"),
            },
        ),
        # Store to save email address entered in popup (memory = resets on page reload)
        dcc.Store(id="email-store", storage_type="memory", data=None),
        # Store to save current result id (memory = resets on page reload)
        dcc.Store(id="current-result-id", storage_type="memory", data=None),
        # Store for dataset name value
        dcc.Store(id="input-dataset", storage_type="memory", data=""),
        html.Div(
            className="get-started",
            children=[
                html.Div(id="popup-container", children=[popup.get_layout(lang)]),
                html.Div(id="popup-done-container", children=[result_ready_popup.get_layout(lang)]),
                html.Div(id="drop-file-section-container", children=[dropFileSection.get_layout(lang)]),
                html.Div(
                    [
                        html.Div(id="climatic-params-layout"),
                        html.Div(id="genetic-params-layout"),
                        html.Div(id="submit-button"),
                    ],
                    id="params-sections",
                ),
            ],
        ),
    ]
)


# Callback to close popup when close button is clicked
@callback(
    Output("popup", "className", allow_duplicate=True),
    Output("popup-dismissed", "data"),
    Input("close-popup-btn", "n_clicks"),
    prevent_initial_call=True,
)
def close_popup(n_clicks):
    """Close the popup when user clicks the X button."""
    if n_clicks:
        return "popup hidden", True
    raise PreventUpdate


# Callback to close result ready popup when close button is clicked
@callback(
    Output("result-ready-popup", "className", allow_duplicate=True),
    Input("close-result-ready-popup-btn", "n_clicks"),
    prevent_initial_call=True,
)
def close_result_ready_popup(n_clicks):
    """Close the result ready popup when user clicks the X button."""
    if n_clicks:
        return "popup hidden"
    raise PreventUpdate


# Callback to poll pipeline status and update UI
@callback(
    Output("popup-status-message", "children"),
    Output("popup-title", "children"),
    Output("popup-icon", "src"),
    Output("pipeline-status-interval", "disabled", allow_duplicate=True),
    Output("global-pipeline-status", "data", allow_duplicate=True),
    Output("popup", "className", allow_duplicate=True),
    Output("result-ready-popup", "className"),
    Output("popup-done-link", "href"),
    Output("popup-email-section", "style"),
    Input("pipeline-status-interval", "n_intervals"),
    State("current-result-id", "data"),
    State("pipeline-started", "data"),
    State("popup-dismissed", "data"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def poll_pipeline_status(n_intervals, result_id, pipeline_started, popup_dismissed, language):
    """
    Poll the background task status and update the UI accordingly.
    Shows current step and estimated time remaining in the popup.
    """
    if not pipeline_started or not result_id:
        raise PreventUpdate

    lang = language if language in LANGUAGE_LIST else "en"

    status_info = background_tasks.get_task_status(result_id)
    status = status_info.get("status", "unknown")
    estimated_time = status_info.get("estimated_time", 0)
    elapsed_time = status_info.get("elapsed_time", 0)

    status_key_map = {
        "pending": "upload.popup.status.pending",
        "complete": "upload.popup.status.complete",
        "error": "upload.popup.status.error",
    }
    key = status_key_map.get(status.lower(), "upload.popup.status.pending")
    base_message = t(key, lang)

    # Add ETA only while it is meaningful; avoid showing "0 sec" before completion.
    if estimated_time > 0 and elapsed_time >= 0:
        remaining_time = estimated_time - elapsed_time
        if remaining_time > 0:
            message = f"{base_message} ({format_remaining_time(remaining_time, lang)})"
        else:
            message = t("upload.popup.status.finalizing", lang)
    else:
        message = base_message

    if status.lower() == "complete":
        return (
            "",
            t("upload.popup.title-complete", lang),
            "",
            True,                        # Disable interval
            status,                      # Update global status
            "popup hidden",              # hide progress popup
            "popup",                     # show result-ready popup
            f"/result/{result_id}",      # popup-done-link href
            {"display": "none"},         # hide email section
        )
    elif status.lower() == "error":
        error_msg = status_info.get("error", "Unknown error")
        if "SPECIMEN_ID_MISMATCH" in error_msg:
            error_msg = t("upload.errors.specimen-id-mismatch", lang)
        popup_class = "popup hidden" if popup_dismissed else "popup"
        return (
            t("upload.popup.error-prefix", lang) + error_msg,
            t("upload.popup.title-error", lang),
            "../../assets/icons/error.svg",
            True,            # Disable interval
            status,          # Update global status
            popup_class,
            "popup hidden",
            dash.no_update,  # popup-done-link href
            {"display": "none"},  # hide email section
        )
    else:
        popup_class = "popup hidden" if popup_dismissed else "popup"
        return (
            message,
            t("upload.popup.title", lang),
            "../../assets/img/coffee-cup.gif",
            False,           # Keep polling
            status,          # Update global status
            popup_class,
            "popup hidden",
            dash.no_update,  # popup-done-link href
            {"display": "block"},  # show email section
        )


@callback(
    Output("drop-file-section-container", "children"),
    Output("popup-container", "children"),
    Output("popup-done-container", "children"),
    Output("genetic-params-layout", "children", allow_duplicate=True),
    Output("climatic-params-layout", "children", allow_duplicate=True),
    Output("submit-button", "children", allow_duplicate=True),
    Input("language-store", "data"),
    State("input-data", "data"),
    prevent_initial_call='initial_duplicate',
)
def update_drop_file_section_language(language, input_data):
    lang = language if language in LANGUAGE_LIST else "en"
    genetic_layout, climatic_layout, submit_layout, _ = rebuild_params_sections_from_store(input_data, lang)
    return (
        [dropFileSection.get_layout(lang)],
        [popup.get_layout(lang)],
        [result_ready_popup.get_layout(lang)],
        genetic_layout,
        climatic_layout,
        submit_layout,
    )


# Callback to save email when user clicks "Send Email" in popup
@callback(
    Output("email-store", "data"),
    Output("toast-store", "data", allow_duplicate=True),
    Input(get_button_id("email-input"), "n_clicks"),
    State("email-input", "value"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def save_email_on_click(n_clicks, email, language):
    """Save email when user clicks Send Email button. Email will be sent when results are ready."""
    lang = language if language in LANGUAGE_LIST else "en"
    if not n_clicks:
        raise PreventUpdate
    if not validate_email(email):
        return None, {"message": t("upload.email.invalid", lang), "type": "error"}
    toast_data = {"message": t("upload.email.notify-on-ready", lang), "type": "success"}
    return email, toast_data


# Callback to send email when results are ready (result_id is set)
@callback(
    Output("consent-choice-store", "data"),
    Input("consent-save-data", "value"),
    prevent_initial_call=True,
)
def sync_consent_choice(consent_choice):
    return consent_choice


@callback(
    Output("email-store", "data", allow_duplicate=True),
    Input("current-result-id", "data"),
    State("email-store", "data"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def send_email_when_results_ready(result_id, email, language):
    """Send email when pipeline finishes and result_id is available."""
    lang = language if language in LANGUAGE_LIST else "en"
    if result_id and email:
        results_url = f"/result/{result_id}"
        mail.send_results_ready_email(email, results_url, lang)
        # Clear email after sending to prevent re-sending
        return None
    raise PreventUpdate


@callback(
    Output("params-climatic", "data"),
    Input("col-analyze", "value"),
    State("params-climatic", "data"),
    prevent_initial_call=True,
)
def params_climatic(column_names, current_data):
    """
    This function fills the params_climatic json object
    args:
        names : names of the columns to use
        current_data : json file containing the current parameters for the climatic data. Should be empty at the beginning

    returns:
        current_data : json file containing the current parameters for the climatic data
    """
    current_data["names"] = column_names
    return current_data


def add_result_to_cookie(result_id):
    """
    Creates a cookie (AUTH) that contains the id of the result.

    args:
        result_id : id of the result

    """
    auth_cookie = request.cookies.get("AUTH")
    response = dash.callback_context.response
    utils.make_cookie(result_id, auth_cookie, response)


# Callback to show uploaded climatic data files
@callback(
    Output("upload-climatic-data", "contents"),
    Output("upload-climatic-data", "filename"),
    Output("upload-climatic-data", "children"),
    Input("upload-climatic-data", "contents"),
    State("upload-climatic-data", "filename"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def uploaded_climatic_data(climatic_data_contents, climatic_data_filename, language):
    """
    This function is called when the user upload climatic data files.
    It displays the name of the file in the upload box.


    Args:
        climatic_data_contents: uploaded climatic data file content in a base64 formatted string.
        climatic_data_filename: name of the uploaded climatic data file
    """
    lang = language if language in LANGUAGE_LIST else "en"

    # Validate file extension
    if CSV_REGEX.fullmatch(climatic_data_filename or "") or EXCEL_REGEX.fullmatch(
        climatic_data_filename or ""
    ):
        return (
            climatic_data_contents,
            climatic_data_filename,
            # Output in climatic data upload box
            html.Div(
                className="loaded-file",
                children=[
                    html.Img(
                        src="../../assets/icons/folder-drop.svg", className="icon"
                    ),
                    html.Div(climatic_data_filename, className="text"),
                ],
            ),
        )
    else:
        return (
            None,
            None,
            # Output in climatic data upload box
            html.Div(
                className="loaded-file error",
                children=[
                    html.Img(
                        src="../../assets/icons/folder-drop.svg", className="icon"
                    ),
                    html.Div(t("upload.file-error-csv-excel", lang), className="text"),
                ],
            ),
        )


# Callback to show uploaded genetic data files
@callback(
    Output("upload-genetic-data", "contents"),
    Output("upload-aligned-genetic-data", "contents"),
    Output("upload-genetic-tree", "contents"),
    Output("upload-genetic-data", "filename"),
    Output("upload-aligned-genetic-data", "filename"),
    Output("upload-genetic-tree", "filename"),
    Output("upload-genetic-data", "children"),
    Output("upload-aligned-genetic-data", "children"),
    Output("upload-genetic-tree", "children"),
    Input("upload-genetic-data", "contents"),
    Input("upload-aligned-genetic-data", "contents"),
    Input("upload-genetic-tree", "contents"),
    State("upload-genetic-data", "filename"),
    State("upload-aligned-genetic-data", "filename"),
    State("upload-genetic-tree", "filename"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def uploaded_genetic_data(
    genetic_data_contents,
    aligned_genetic_data_contents,
    genetic_tree_contents,
    genetic_data_filename,
    aligned_genetic_data_filename,
    genetic_tree_filename,
    language,
):
    """
    This function is called when the user upload genetic data files.
    It displays the name of the file in the upload box and clear files
    from any subsequent upload that are from the same type.

    (Ex. If a genetic data file is uploaded and the user upload a genetic tree,
    the genetic data file with be nulled, and vice versa. Same for aligned genetic data file if uploaded.)

    Args:
        genetic_data_contents: uploaded genetic data file content in a base64 formatted string.
        aligned_genetic_data_contents: uploaded aligned genetic data file content in a base64 formatted string.
        genetic_tree_contents: uploaded genetic tree file content in a base64 formatted string.
        genetic_data_filename: name of the uploaded genetic data file
        aligned_genetic_data_filename: name of the uploaded aligned genetic data file
        genetic_tree_filename: name of the uploaded genetic tree file
    """

    lang = language if language in LANGUAGE_LIST else "en"

    def default_upload_child(file_types):
        return html.Div(
            [
                html.Img(
                    src="../../assets/icons/folder-drop.svg",
                    className="drop-icon",
                ),
                html.Div(t("upload.drag-drop", lang), className="drop-main-text"),
                html.Div(t("upload.click-browse", lang), className="drop-sub-text"),
                create_badge(
                    text=file_types,
                    background_color="var(--action-soft-bg)",
                    text_color="var(--action)",
                ),
            ],
            className="drop-content-inner",
        )

    def loaded_upload_child(text, is_error=False):
        class_name = "loaded-file error" if is_error else "loaded-file"
        return html.Div(
            className=class_name,
            children=[
                html.Img(src="../../assets/icons/folder-drop.svg", className="icon"),
                html.Div(text, className="text"),
            ],
        )

    genetic_default = default_upload_child(".fasta")
    aligned_default = default_upload_child(".fasta, .json")
    tree_default = default_upload_child(".json")

    upload_box = dash.callback_context.triggered_id

    if upload_box == "upload-genetic-data":
        if FASTA_REGEX.fullmatch(genetic_data_filename or ""):
            return (
                genetic_data_contents,
                None,
                None,
                genetic_data_filename,
                None,
                None,
                loaded_upload_child(genetic_data_filename),
                aligned_default,
                tree_default,
            )
        else:
            return (
                None,
                None,
                None,
                None,
                None,
                None,
                loaded_upload_child(t("upload.file-error-fasta", lang), is_error=True),
                aligned_default,
                tree_default,
            )
    elif upload_box == "upload-aligned-genetic-data":
        if JSON_REGEX.fullmatch(aligned_genetic_data_filename or "") or FASTA_REGEX.fullmatch(aligned_genetic_data_filename or ""):
            return (
                None,
                aligned_genetic_data_contents,
                None,
                None,
                aligned_genetic_data_filename,
                None,
                genetic_default,
                loaded_upload_child(aligned_genetic_data_filename),
                tree_default,
            )
        else:
            return (
                None,
                None,
                None,
                None,
                None,
                None,
                genetic_default,
                loaded_upload_child(t("upload.file-error-json", lang), is_error=True),
                tree_default,
            )
    elif upload_box == "upload-genetic-tree":
        if JSON_REGEX.fullmatch(genetic_tree_filename or ""):
            return (
                None,
                None,
                genetic_tree_contents,
                None,
                None,
                genetic_tree_filename,
                genetic_default,
                aligned_default,
                loaded_upload_child(genetic_tree_filename),
            )
        else:
            return (
                None,
                None,
                None,
                None,
                None,
                None,
                genetic_default,
                aligned_default,
                loaded_upload_child(t("upload.file-error-json", lang), is_error=True),
            )


@callback(
    Output("genetic-params-layout", "children"),
    Output("climatic-params-layout", "children"),
    Output("submit-button", "children"),
    Output("input-data", "data"),
    Output("toast-store", "data", allow_duplicate=True),
    Input("next-button", "n_clicks"),
    Input("upload-test-data", "n_clicks"),
    State("language-store", "data"),
    State("upload-genetic-data", "contents"),
    State("upload-genetic-data", "filename"),
    State("upload-genetic-data", "last_modified"),
    State("upload-aligned-genetic-data", "contents"),
    State("upload-aligned-genetic-data", "filename"),
    State("upload-aligned-genetic-data", "last_modified"),
    State("upload-genetic-tree", "contents"),
    State("upload-genetic-tree", "filename"),
    State("upload-genetic-tree", "last_modified"),
    State("upload-climatic-data", "contents"),
    State("upload-climatic-data", "filename"),
    State("upload-climatic-data", "last_modified"),
    State("input-data", "data"),
    prevent_initial_call=True,
)
def upload_data(
    next_n_clicks,
    test_n_clicks,
    language,
    genetic_data_contents,
    genetic_data_filename,
    genetic_data_last_modified,
    aligned_genetic_data_contents,
    aligned_genetic_data_filename,
    aligned_genetic_data_last_modified,
    genetic_tree_contents,
    genetic_tree_filename,
    genetic_tree_last_modified,
    climatic_data_contents,
    climatic_data_filename,
    climatic_data_last_modified,
    current_data,
):
    """
    This function is called when the "Next" button is clicked. For genetic data and climatic data,
    it shows the graph sections and it upload the contents of the upload boxes in the 'input-data' store element.

    Args:
        n_clicks: the number of clicks of the next-button
        genetic_data_contents: the genetic data in the base64 string format from Dash Upload
        genetic_data_filename: genetic data file name
        genetic_data_last_modified: genetic data 'last modified' timestamp
        aligned_genetic_data_contents: the aligned genetic data in the base64 string format from Dash Upload
        aligned_genetic_data_filename: aligned genetic data file name
        aligned_genetic_data_last_modified: aligned genetic data 'last modified' timestamp
        genetic_tree_contents: the genetic tree in the base64 string format from Dash Upload
        genetic_tree_filename: genetic tree file name
        genetic_tree_last_modified: genetic tree 'last modified' timestamp
        climatic_data_contents: the climatic data in the base64 string format from Dash Upload
        climatic_data_filename: climatic data file name
        climatic_data_last_modified: climatic data 'last modified' timestamp
        current_data: content from the Dash Store element called 'input-data'

    Returns:
        the layouts to show on the page, and
        the update content from uploaded files to the Dash Store element 'input-data'
    """
    lang = language if language in LANGUAGE_LIST else "en"
    button_clicked = ctx.triggered_id
    genetic_layout = ""
    climatic_layout = ""

    if button_clicked in ["next-button", "upload-test-data"]:
        click_count = next_n_clicks if button_clicked == "next-button" else test_n_clicks
        if (click_count is None or click_count == 0) and current_data.get("submit button"):
            return rebuild_params_sections_from_store(current_data, lang)

    genetic_data_is_present = (
        genetic_data_contents is not None and genetic_data_contents != ""
    )
    aligned_genetic_data_is_present = (
        aligned_genetic_data_contents is not None and aligned_genetic_data_contents != ""
    )
    genetic_tree_is_present = (
        genetic_tree_contents is not None and genetic_tree_contents != ""
    )
    climatic_data_is_present = (
        climatic_data_contents is not None and climatic_data_contents != ""
    )
    climatic_data_to_show = False
    genetic_data_to_show = False
    climatic_data_is_missing = not climatic_data_is_present
    genetic_data_is_missing = (
        not genetic_data_is_present and not aligned_genetic_data_is_present and not genetic_tree_is_present
    )

    if button_clicked == "next-button" and (
        climatic_data_is_missing or genetic_data_is_missing
    ):
        raise PreventUpdate

    submit_button = submitButton.get_layout(lang) if current_data.get("submit button") else ""
    if not current_data["submit button"] and button_clicked in ["next-button", "upload-test-data"]:
        current_data["submit button"] = True
        submit_button = submitButton.get_layout(lang)

    if button_clicked == "upload-test-data":
        # Test data example "Don't know where to start?"
        # Show graph for genetic data
        parsed_genetic_file = parse_uploaded_files(
            CONTENT_GENETIC, "seq very small.fasta"
        )
        current_data["genetic"]["file"] = parsed_genetic_file[
            "dataframe"
        ]  # dict key=  value= fasta strings
        genetic_layout = paramsGenetic.get_layout(
            parsed_genetic_file["dataframe"],
            lang,
        )
        current_data["genetic"]["file_name"] = "seq very small.fasta"
        current_data["genetic"]["last_modified_date"] = 1680370585.9890237
        genetic_data_to_show = True
        # Change aligned genetic data and genetic tree to None
        current_data["aligned_genetic"]["file"] = None
        current_data["aligned_genetic"]["file_name"] = None
        current_data["aligned_genetic"]["last_modified_date"] = None
        current_data["aligned_genetic"]["file_name"] = None
        current_data["genetic_tree"]["file"] = None
        current_data["genetic_tree"]["file_name"] = None
        current_data["genetic_tree"]["last_modified_date"] = None
        # Show graph for climatic data
        # Show graphs, table and columns to choose
        parsed_climatic_file = parse_uploaded_files(CONTENT_CLIMATIC, "geo.csv")
        current_data["climatic"]["file"] = parsed_climatic_file[
            "dataframe"
        ].to_json()  # json of a pandas dataframe
        climatic_layout = paramsClimatic.create_table(
            parsed_climatic_file["dataframe"],
            lang,
        )
        current_data["climatic"]["file_name"] = "geo.csv"
        current_data["climatic"]["last_modified_date"] = 1680370585.9880235
        climatic_data_to_show = True

    elif button_clicked == "next-button":
        if genetic_data_is_present:
            # Show graph
            parsed_genetic_file = parse_uploaded_files(
                genetic_data_contents, genetic_data_filename
            )
            current_data["genetic"]["file"] = parsed_genetic_file[
                "dataframe"
            ]  # dict key=  value= fasta strings
            genetic_layout = paramsGenetic.get_layout(
                parsed_genetic_file["dataframe"],
                lang,
            )
            current_data["genetic"]["file_name"] = genetic_data_filename
            current_data["genetic"]["last_modified_date"] = genetic_data_last_modified
            genetic_data_to_show = True
            # Change aligned genetic data and genetic tree to None
            current_data["aligned_genetic"]["file"] = None
            current_data["aligned_genetic"]["file_name"] = None
            current_data["aligned_genetic"]["last_modified_date"] = None
            current_data["genetic_tree"]["file"] = None
            current_data["genetic_tree"]["file_name"] = None
            current_data["genetic_tree"]["last_modified_date"] = None
        elif aligned_genetic_data_is_present:
            # Won't show any graphs
            parsed_aligned_genetic_file = parse_uploaded_files(
                aligned_genetic_data_contents, aligned_genetic_data_filename, is_aligned=True, lang=lang
            )
            if parsed_aligned_genetic_file is None or "error" in parsed_aligned_genetic_file:
                error_msg = (parsed_aligned_genetic_file or {}).get(
                    "error", "Failed to parse aligned genetic file."
                )
                return "", "", "", current_data, {"message": error_msg, "type": "error"}
            current_data["aligned_genetic"]["file"] = parsed_aligned_genetic_file[
                "dataframe"
            ]  # json object
            current_data["aligned_genetic"]["type"] = parsed_aligned_genetic_file["type"]
            current_data["aligned_genetic"]["file_name"] = aligned_genetic_data_filename
            current_data["aligned_genetic"][
                "last_modified_date"
            ] = aligned_genetic_data_last_modified
            genetic_data_to_show: False
            # Change genetic data and genetic tree to None
            current_data["genetic"]["file"] = None
            current_data["genetic"]["file_name"] = None
            current_data["genetic"]["last_modified_date"] = None
            current_data["genetic_tree"]["file"] = None
            current_data["genetic_tree"]["file_name"] = None
            current_data["genetic_tree"]["last_modified_date"] = None
        elif genetic_tree_is_present:
            # Won't show any graphs
            parsed_genetic_tree_file = parse_uploaded_files(
                genetic_tree_contents, genetic_tree_filename
            )
            current_data["genetic_tree"]["file"] = parsed_genetic_tree_file[
                "dataframe"
            ]  # json object
            current_data["genetic_tree"]["type"] = parsed_genetic_tree_file["type"]
            current_data["genetic_tree"]["file_name"] = genetic_tree_filename
            current_data["genetic_tree"][
                "last_modified_date"
            ] = genetic_tree_last_modified
            genetic_data_to_show: False
            # Change aligned genetic data and genetic data to None
            current_data["genetic"]["file"] = None
            current_data["genetic"]["file_name"] = None
            current_data["genetic"]["last_modified_date"] = None
            current_data["aligned_genetic"]["file"] = None
            current_data["aligned_genetic"]["file_name"] = None
            current_data["aligned_genetic"]["last_modified_date"] = None

        if climatic_data_is_present:
            # Show graphs, table and columns to choose
            parsed_climatic_file = parse_uploaded_files(
                climatic_data_contents, climatic_data_filename
            )
            current_data["climatic"]["file"] = parsed_climatic_file[
                "dataframe"
            ].to_json()  # json of a pandas dataframe
            climatic_layout = paramsClimatic.create_table(
                parsed_climatic_file["dataframe"],
                lang,
            )
            current_data["climatic"]["file_name"] = climatic_data_filename
            current_data["climatic"]["last_modified_date"] = climatic_data_last_modified
            climatic_data_to_show = True

    if climatic_data_to_show and genetic_data_to_show:
        return genetic_layout, climatic_layout, submit_button, current_data, None
    elif climatic_data_to_show:
        return "", climatic_layout, submit_button, current_data, None
    elif genetic_data_to_show:
        return genetic_layout, "", submit_button, current_data, None
    else:
        return "", "", submit_button, current_data, None


def parse_uploaded_files(content, file_name, is_aligned=False, lang="en"):
    """
    Parse a base64 string into the proper format to pass through the aPhyloGeo pipeline

    Args:
        content (base64 string): uploaded content from Dash Upload Module
        file_name (string): file name
        is_aligned (bool): True if the file is pre-aligned genetic data

    """
    results = {}

    try:
        content_type, content_string = content.split(",")
        decoded_content = base64.b64decode(content_string)

        if content_type in [
            "data:text/csv;base64",
            "data:application/vnd.ms-excel;base64",
        ]:
            # Assume that the user uploaded a CSV file (climatic data)
            results["type"] = "csv"
            results["dataframe"] = pd.read_csv(
                io.StringIO(decoded_content.decode("utf-8"))
            )
        elif EXCEL_REGEX.fullmatch(file_name):
            # Assume that the user uploaded an excel file (climatic data)
            results["type"] = "excel"
            results["dataframe"] = pd.read_excel(io.BytesIO(decoded_content))
        elif FASTA_REGEX.fullmatch(file_name):
            fasta_file_string = decoded_content.decode("utf-8").replace("\r\n", "\n")
            if is_aligned:
                # Pre-aligned FASTA: convert to Alignment JSON so the pipeline
                # can skip the alignment step and go straight to tree building.
                # AlignIO.read requires all sequences to have the same length —
                # if they don't, the file is not actually aligned.
                try:
                    msa = AlignIO.read(io.StringIO(fasta_file_string), "fasta")
                except ValueError:
                    results["error"] = t("upload.file-error-not-aligned", lang)
                    return results
                # Import lazily to avoid loading deprecated Bio.Application wrappers at startup.
                from aphylogeo.alignement import Alignment as AlignmentClass

                alignment_obj = AlignmentClass("0", {"0": msa})
                results["type"] = "json"
                results["dataframe"] = json.dumps(alignment_obj.to_dict())
            else:
                # Regular FASTA that needs alignment
                results["type"] = "fasta"
                results["dataframe"] = files_ctrl.fasta_to_str(
                    SeqIO.parse(io.StringIO(fasta_file_string), "fasta")
                )
                # Save the fasta file (needed for aPhyloGeo Alignment)
                with open("./temp/genetic_data.fasta", "w") as f:
                    f.write(fasta_file_string)
        elif content_type == "data:application/json;base64" or JSON_REGEX.fullmatch(file_name):
            # JSON file — detected by MIME type or filename extension.
            # Some browsers send .json as application/octet-stream, so the
            # filename fallback prevents silent upload failures.
            results["type"] = "json"
            results["dataframe"] = decoded_content.decode("utf-8")

        results["base64"] = content_string

        return results

    except Exception as e:
        print(e)


def rebuild_params_sections_from_store(current_data, lang):
    genetic_layout = ""
    climatic_layout = ""

    if current_data["genetic"]["file"] is not None:
        genetic_layout = paramsGenetic.get_layout(
            current_data["genetic"]["file"],
            lang,
        )

    if current_data["climatic"]["file"] is not None:
        climatic_df = pd.read_json(io.StringIO(current_data["climatic"]["file"]))
        climatic_layout = paramsClimatic.create_table(
            climatic_df,
            lang,
        )

    submit_layout = submitButton.get_layout(lang) if current_data.get("submit button") else ""

    return genetic_layout, climatic_layout, submit_layout, current_data


@callback(
    Output("popup", "className", allow_duplicate=True),
    Output("column-error-message", "children"),
    Output("name-error-message", "children"),
    Output("consent-error-message", "children"),
    Output("ready-for-pipeline", "data"),
    Output("result-name-store", "data"),
    [
        Input("submit-dataset", "n_clicks"),
        Input("input-dataset-visible", "value"),
    ],
    State("input-data", "data"),
    State("params-climatic", "data"),
    State("consent-choice-store", "data"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def ready_for_pipeline(
    open, result_name, input_data, params_climatic, consent_save_data, language
):
    """
    Verify the following prerequisites needed for aPhyloGeo pipeline to start:
    - At least one column is selected from the climatic data file.
     - The dataset has a name.
     - Verify the presence of uploaded climatic and genetic data.


    Args:
        open : counter of the submit button
        result_name : name of the results that will be generated
        input_data: input_data : json file containing the data from the uploaded files
        params_climatic: parameters for the climatic data

    Returns:
        className : class of the popup if the inputs are valid
        column-error-message : NUMBER_OF_COLUMNS_ERROR_MESSAGE if the number of columns is not valid
        name_error_message : NAME_ERROR_MESSAGE if the name of the results is not valid
        ready-for-pipeline: True if all prerequisites are met for aPhyloGeo pipeline to start, else False
    """
    lang = language if language in LANGUAGE_LIST else "en"

    # Add climatic column names to Params
    if params_climatic["names"] is not None:
        names = ["id"] + params_climatic["names"]
        params_climatic["names"] = names
        Params.names = names

    # Assure there is at least one genetic file and one climatic file uploaded
    files_are_present = (
        input_data["genetic"]["file"] is not None or input_data["aligned_genetic"]["file"] is not None or input_data["genetic_tree"]["file"] is not None
    ) and (input_data["climatic"]["file"] is not None)

    climatic_data_is_present = input_data["climatic"]["file"] is not None

    if open is None or open < 1 or not files_are_present:
        raise PreventUpdate

    trigger_id = ctx.triggered_id

    # if trigger_id == "close_popup":
    #     return 'popup hidden', '', '', False

    # Assure there is a dataset name given by the user
    result_name_is_valid = result_name is not None and result_name != ""
    params_climatic_is_complete = (
        params_climatic["names"] is not None and len(params_climatic["names"]) >= 2
    )

    column_error = (
        t("upload.errors.number-of-columns", lang)
        if climatic_data_is_present and not params_climatic_is_complete
        else ""
    )
    name_error = (
        t("upload.errors.name-required", lang) if not result_name_is_valid else ""
    )
    consent_error = (
        "" if consent_save_data in {"granted", "declined"} else t("upload.errors.consent-required", lang)
    )

    if column_error or name_error or consent_error:
        return (
            "popup hidden",
            column_error,
            name_error,
            consent_error,
            False,
            dash.no_update,
        )

    if trigger_id != "submit-dataset":
        return "", "", "", "", False, dash.no_update

    return "popup", "", "", "", True, result_name


@callback(
    Output("column-error-message", "children", allow_duplicate=True),
    Input("col-analyze", "value"),
    prevent_initial_call=True,
)
def clear_column_error_when_valid(column_names):
    """Clear the column error as soon as at least one column is selected."""
    if column_names is not None and len(column_names) >= 1:
        return ""
    return dash.no_update


@callback(
    Output("consent-error-message", "children", allow_duplicate=True),
    Input("consent-choice-store", "data"),
    prevent_initial_call=True,
)
def clear_consent_error_when_selected(consent_value):
    if consent_value in {"granted", "declined"}:
        return ""
    return dash.no_update


@callback(
    Output("popup", "className", allow_duplicate=True),
    Output("current-result-id", "data"),
    Output("pipeline-started", "data"),
    Output("pipeline-status-interval", "disabled"),
    Output("global-pipeline-status", "data", allow_duplicate=True),
    Output("global-result-id", "data", allow_duplicate=True),
    Output("global-pipeline-interval", "disabled", allow_duplicate=True),
    Output("progress-bar", "className", allow_duplicate=True),
    Output("progress-bar-fill", "style", allow_duplicate=True),
    Output("popup-dismissed", "data", allow_duplicate=True),
    Output("ready-for-pipeline", "data", allow_duplicate=True),
    Input("ready-for-pipeline", "data"),
    State("input-data", "data"),
    State("params-climatic", "data"),
    State("params-genetic", "data"),
    State("result-name-store", "data"),
    State("email-store", "data"),
    State("consent-choice-store", "data"),
    State("language-store", "data"),
    prevent_initial_call=True,
)
def submit_button(
    ready_for_pipeline, input_data, params_climatic, params_genetic, result_name, email, consent_save_data, language
):
    """
    Starts the pipeline asynchronously when all prerequisites are met.
    Returns immediately so the user can navigate elsewhere.
    """
    _NO_UPDATE = (
        dash.no_update, dash.no_update, dash.no_update, dash.no_update,
        dash.no_update, dash.no_update, dash.no_update, dash.no_update,
        dash.no_update, dash.no_update, dash.no_update,
    )
    _ERROR_RETURN = (
        "popup",
        dash.no_update, dash.no_update, dash.no_update,
        dash.no_update, dash.no_update, dash.no_update,
        dash.no_update, dash.no_update,
        False, False,
    )

    if not ready_for_pipeline:
        return _NO_UPDATE

    has_storage_consent = consent_save_data == "granted"

    if not has_storage_consent and not results_ctrl.is_temp_storage_available():
        return _ERROR_RETURN

    # Map each input key → (files_ids key, result_type label)
    FILE_SLOTS = [
        ("climatic", "climatic_files_id", "climatic"),
        ("genetic", "genetic_files_id", "genetic"),
        ("aligned_genetic", "aligned_genetic_files_id", "genetic"),
        ("genetic_tree", "genetic_tree_files_id", "genetic"),
    ]

    try:
        result_type = []
        files_ids = {}
        for slot_key, files_key, type_label in FILE_SLOTS:
            if input_data[slot_key]["file"] is not None:
                if has_storage_consent:
                    files_ids[files_key] = utils.save_files(input_data[slot_key])
                if type_label not in result_type:
                    result_type.append(type_label)

        # Create either a persisted result or a temporary Redis-backed result.
        result_id = utils.create_result(
            files_ids,
            result_type,
            params_climatic,
            params_genetic,
            result_name,
            temporary=not has_storage_consent,
        )

        add_result_to_cookie(result_id)

        background_tasks.run_pipeline_async(
            result_id=result_id,
            climatic_file=input_data["climatic"]["file"],
            genetic_file=input_data["genetic"]["file"],
            aligned_genetic_file=input_data["aligned_genetic"]["file"],
            genetic_tree_file=input_data["genetic_tree"]["file"],
            params_climatic=params_climatic,
            email=email,
        )

        return (
            "popup",          # popup className
            result_id,        # current-result-id
            True,             # pipeline-started
            False,            # pipeline-status-interval disabled
            "running",        # global-pipeline-status
            result_id,        # global-result-id
            False,            # global-pipeline-interval disabled
            "progress-bar",   # progress-bar className
            {"width": "0%"},  # progress-bar-fill style
            False,            # popup-dismissed reset
            False,            # ready-for-pipeline reset
        )
    except Exception as e:
        print(f"[submit_button] Error: {e}")
        return _ERROR_RETURN
