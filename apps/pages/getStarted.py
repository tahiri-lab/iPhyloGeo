import os
import re
from dash import dcc, html, State, Input, Output, callback, ctx
import dash
from dash.exceptions import PreventUpdate
from dotenv import dotenv_values
from flask import request
import dash_bootstrap_components as dbc
import pages.upload.dropFileSection as dropFileSection
import utils.utils as utils
import pages.upload.climatic.paramsClimatic as paramsClimatic
import pages.upload.genetic.paramsGenetic as paramsGenetic
import pages.upload.submitButton as submitButton
import pages.utils.popup as popup
import pages.utils.popupDone as popupDone
import json
import pandas as pd
import base64
import io
from Bio import SeqIO
import db.controllers.files as files_ctrl
import db.controllers.results as results_ctrl
from aphylogeo.params import Params
from aphylogeo.alignement import Alignment
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aphylogeo.genetic_trees import GeneticTrees

# Load genetic settings from genetic settings file (YAML)
genetic_setting_file = json.load(open('genetic_settings_file.json', 'r'))

#Update Params for aPhyloGeo
Params.update_from_dict(genetic_setting_file)

CONTENT_CLIMATIC = "data:text/csv;base64,aWQsQUxMU0tZX1NGQ19TV19EV04sVDJNLFFWMk0sUFJFQ1RPVENPUlIsV1MxME0NCk9NNzM5MDUzLDQuNywxNC44MDMzMzMzMzMzMzMzMzUsNi43MTMzMzMzMzMzMzMzMzQsMS42MjMzMzMzMzMzMzMzMzMsMi41NTMzMzMzMzMzMzMzMzMyDQpPVTQ3MTA0MCwxLjQ2LDQuMTksNC41MTY2NjY2NjY2NjY2NjcsMC4xMiwzLjA0MzMzMzMzMzMzMzMzMw0KT04xMjk0MjksNi44OTMzMzMzMzMzMzMzMzM1LDI3LjA2NjY2NjY2NjY2NjY2NiwxNS4xNTY2NjY2NjY2NjY2NjUsMC43MTY2NjY2NjY2NjY2NjY3LDEuMzYNCk9MOTg5MDc0LDQuNjQ2NjY2NjY2NjY2NjY2NSwyNi4xMiwxOC4xMDY2NjY2NjY2NjY2NzYsMC40NzMzMzMzMzMzMzMzMzM0LDUuNjYNCk9OMTM0ODUyLDYuODQwMDAwMDAwMDAwMDAyNSwxNi45NzMzMzMzMzMzMzMzMzMsNS41NzY2NjY2NjY2NjY2NjcsMC40OTY2NjY2NjY2NjY2NjY2LDQuNjY2NjY2NjY2NjY2NjY3"
CONTENT_GENETIC = "data:application/octet-stream;base64,Pk9OMTI5NDI5DQpBQ1RUVENHQVRDVENUVEdUQUdBVENUR1RUQ1RDVEFBQUNHQUFDVFRUQUFBQVRDVEdUR1RHR0NUR1RDQUMNClRDR0dDVEdDQVRHQ1RUQUdUR0NBQ1RDQUNHQ0FHVEFUQUFUVEFBVEFBQ1RBQVRUQUNUR1RDR1RUR0FDQQ0KR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQ1RUQ1RHQ0FHR0NUR0NUVEFDR0dUVFRDR1RDQ0dUR1RUR0NBR0NDDQpHQVRDQVRDQUdDQUNBVENUQUdHVFRUVEdUQ0NHR0dUR1RHQUNDR0FBQUdHVEFBR0FUR0dBR0FHQ0NUVEcNClRDQ0NUR0dUVFRDQUFDR0FHQUFBQUNBQ0FDR1RDQ0FBQ1RDQUdUVFRHQ0NUR1RUVFRBQ0FHR1RUQ0dDRw0KQUNHVEdDVENHVEFDR1RHR0NUVFRHR0FHQUNUQ0NHVEdHQUdHQUdHVENUVEFUQ0FHQUdHQ0FDR1RDQUFDDQpBVENUVEFBQUdBVEdHQ0FDVFRHVEdHQ1RUQUdUQUdBQUdUVEdBQUFBQUdHQ0dUVFRUR0NDVENBQUNUVEcNCkFBQ0FHQ0NDVEFUR1RHVFRDQVRDQUFBQ0dUVENHR0FUR0NUQ0dBQUNUR0NBQ0NUQ0FUR0dUQ0FUR1RUQQ0KVEdHVFRHQVRDVEdHVEFHQ0FHQUFDVENHQUFHR0NBVFRDQUdUQUNHR1RDR1RBR1RHR1RHQUdBQ0FDVFRHDQpHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHQ0dBQUFUQUNDQUdUR0dDVFRBQ0NHQ0FBR0dUVENUVENUVENHVEENCkFHQUFDR0dUQUFUQUFBR0dBR0NUR0dUR0dDQ0FUQUdUVEFDR0dDR0NDR0FUQ1RBQUFHVENBVFRUR0FDVA0KVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQVRDQ1RUQVRHQUFHQVRUVFRDQUFHQUFBQUNUR0dBQUNBQ1RBQUFDDQpBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBQUNUQ0FUR0NHVEdBR0NUVEFBQ0dHQUdHR0dDVFRBQ0FDVENHQ1QNCkFUR1RDR0FUQUFDQUFDVFRDVEdUR0dDQ0NUR0FUR0dDVEFDQ0NUQ1RUR0FHVEdDQVRUQUFBR0FDQ1RUQw0KVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQ0FUR0NBQ1RUVEdUQ1RHQUFDQUFDVEdHQUNUVFRBVFRHQUNBQ1RBDQpBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHVEdBQUNBVEdBR0NBVEdBQUFUVEdDVFRHR1RBQ0FDR0dBQUNHVFQNCkNUR0FBQUFHQUdDVEFUR0FBVFRHQ0FHQUNBQ0NUVFRUR0FBQVRUQUFBVFRHR0NBQUFHQUFBVFRUR0FDQQ0KQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQVRUVFRHVEFUVFRDQ0NUVEFBQVRUQ0NBVEFBVENBQUdBQ1RBVFRDDQpBQUNDQUFHR0dUVEdBQUFBR0FBQUFBR0NUVEdBVEdHQ1RUVEFUR0dHVEFHQUFUVENHQVRDVEdUQ1RBVEMNCkNBR1RUR0NHVENBQ0NBQUFUR0FBVEdDQUFDQ0FBQVRHVEdDQ1RUVENBQUNUQ1RDQVRHQUFHVEdUR0FUQw0KQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQUdBQ0dHR0NHQVRUVFRHVFRBQUFHQ0NBQ1RUR0NHQUFUVFRUR1RHDQo+T04xMzQ4NTINCkFHQVRDVEdUVENUQ1RBQUFDR0FBQ1RUVEFBQUFUQ1RHVEdUR0dDVEdUQ0FDVENHR0NUR0NBVEdDVFRBRw0KVEdDQUNUQ0FDR0NBR1RBVEFBVFRBQVRBQUNUQUFUVEFDVEdUQ0dUVEdBQ0FHR0FDQUNHQUdUQUFDVENHDQpUQ1RBVENUVENUR0NBR0dDVEdDVFRBQ0dHVFRUQ0dUQ0NHVEdUVEdDQUdDQ0dBVENBVENBR0NBQ0FUQ1QNCkFHR1RUVFRHVENDR0dHVEdUR0FDQ0dBQUFHR1RBQUdBVEdHQUdBR0NDVFRHVENDQ1RHR1RUVENBQUNHQQ0KR0FBQUFDQUNBQ0dUQ0NBQUNUQ0FHVFRUR0NDVEdUVFRUQUNBR0dUVENHQ0dBQ0dUR0NUQ0dUQUNHVEdHDQpDVFRUR0dBR0FDVENDR1RHR0FHR0FHR1RDVFRBVENBR0FHR0NBQ0dUQ0FBQ0FUQ1RUQUFBR0FUR0dDQUMNClRUR1RHR0NUVEFHVEFHQUFHVFRHQUFBQUFHR0NHVFRUVEdDQ1RDQUFDVFRHQUFDQUdDQ0NUQVRHVEdUVA0KQ0FUQ0FBQUNHVFRDR0dBVEdDVENHQUFDVEdDQUNDVENBVEdHVENBVEdUVEFUR0dUVEdBR0NUR0dUQUdDDQpBR0FBQ1RDR0FBR0dDQVRUQ0FHVEFDR0dUQ0dUQUdUR0dUR0FHQUNBQ1RUR0dUR1RDQ1RUR1RDQ0NUQ0ENClRHVEdHR0NHQUFBVEFDQ0FHVEdHQ1RUQUNDR0NBQUdHVFRDVFRDVFRDR1RBQUdBQUNHR1RBQVRBQUFHRw0KQUdDVEdHVEdHQ0NBVEFHVFRBQ0dHQ0dDQ0dBVENUQUFBR1RDQVRUVEdBQ1RUQUdHQ0dBQ0dBR0NUVEdHDQpDQUNUR0FUQ0NUVEFUR0FBR0FUVFRUQ0FBR0FBQUFDVEdHQUFDQUNUQUFBQ0FUQUdDQUdUR0dUR1RUQUMNCkNDR1RHQUFDVENBVEdDR1RHQUdDVFRBQUNHR0FHR0dHQ0FUQUNBQ1RDR0NUQVRHVENHQVRBQUNBQUNUVA0KQ1RHVEdHQ0NDVEdBVEdHQ1RBQ0NDVENUVEdBR1RHQ0FUVEFBQUdBQ0NUVENUQUdDQUNHVEdDVEdHVEFBDQpBR0NUVENBVEdDQUNUVFRHVENDR0FBQ0FBQ1RHR0FDVFRUQVRUR0FDQUNUQUFHQUdHR0dUR1RBVEFDVEcNCkNUR0NDR1RHQUFDQVRHQUdDQVRHQUFBVFRHQ1RUR0dUQUNBQ0dHQUFDR1RUQ1RHQUFBQUdBR0NUQVRHQQ0KQVRUR0NBR0FDQUNDVFRUVEdBQUFUVEFBQVRUR0dDQUFBR0FBQVRUVEdBQ0FDQ1RUQ0FBVEdHR0dBQVRHDQpUQ0NBQUFUVFRUR1RBVFRUQ0NDVFRBQUFUVENDQVRBQVRDQUFHQUNUQVRUQ0FBQ0NBQUdHR1RUR0FBQUENCkdBQUFBQUdDVFRHQVRHR0NUVFRBVEdHR1RBR0FBVFRDR0FUQ1RHVENUQVRDQ0FHVFRHQ0dUQ0FDQ0FBQQ0KVEdBQVRHQ0FBQ0NBQUFUR1RHQ0NUVFRDQUFDVENUQ0FUR0FBR1RHVEdBVENBVFRHVEdHVEdBQUFDVFRDDQpBVEdHQ0FHQUNHR0dDR0FUVFRUR1RUQUFBR0NDQUNUVEdDR0FBVFRUVEdUR0dDQUNUR0FHQUFUVFRHQUMNClQNCj5PTDk4OTA3NA0KQVRUQUFBR0dUVFRBVEFDQ1RUQ0NDQUdHVEFBQ0FBQUNDQUFDQ0FBQ1RUVENHQVRDVENUVEdUQUdBVENUDQpHVFRDVFRUQUFBQ0dBQUNUVFRBQUFBVENUR1RHVEdHQ1RHVENBQ1RDR0dDVEdDQVRHQ1RUQUdUR0NBQ1QNCkNBQ0dDQUdUQVRBQVRUQUFUQUFDVEFBVFRBQ1RHVENHVFRHQUNBR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQw0KVFRDVEdDQUdHQ1RHQ1RUQUNHR1RUVENHVENDR1RHVFRHQ0FHQ0NHQVRDQVRDQUdDQUNBVENUQUdHVFRUDQpUR1RDQ0dHR1RHVEdBQ0NHQUFBR0dUQUFHQVRHR0FHQUdDQ1RUR1RDQ0NUR0dUVFRDQUFDR0FHQUFBQUMNCkFDQUNHVENDQUFDVENBR1RUVEdDQ1RHVFRUVEFDQUdHVFRDR0NHQUNHVEdDVENHVEFDR1RHR0NUVFRHRw0KQUdBQ1RDQ0dUR0dBR0dBR0dUQ1RUQVRDQUdBR0dDQUNHVENBQUNBVENUVEFBQUdBVEdHQ0FDVFRHVEdHDQpDVFRBR1RBR0FBR1RUR0FBQUFBR0dDR1RUVFRHQ0NUQ0FBQ1RUR0FBQ0FHQ0NDVEFUR1RHVFRDQVRDQUENCkFDR1RUQ0dHQVRHQ1RDR0FBQ1RHQ0FDQ1RDQVRHR1RDQVRHVFRBVEdHVFRHQUdDVEdHVEFHQ0FHQUFDVA0KQ0dBQUdHQ0FUVENBR1RBQ0dHVENHVEFHVEdHVEdBR0FDQUNUVEdHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHDQpDR0FBQVRBQ0NBR1RHR0NUVEFDQ0dDQUFHR1RUQ1RUQ1RUQ0dUQUFHQUFDR0dUQUFUQUFBR0dBR0NUR0cNClRHR0NDQVRBR1RUQUNHR0NHQ0NHQVRDVEFOTk5OTk5OTk5HQUNUVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQQ0KVENDVFRBVEdBQUdBVFRUVENBQUdBQUFBQ1RHR0FBQ0FDVEFBQUNBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBDQpBQ1RDQVRHQ0dUR0FHQ1RUQUFDR0dBR0dHR0NBVEFDQUNUQ0dDVEFUR1RDR0FUQUFDQUFDVFRDVEdUR0cNCkNDQ1RHQVRHR0NUQUNDQ1RDVFRHQUdUR0NBVFRBQUFHQUNDVFRDVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQw0KQVRHQ0FDVFRUR1RDQ0dBQUNBQUNUR0dBQ1RUVEFUVEdBQ0FDVEFBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHDQpUR0FBQ0FUR0FHQ0FUR0FBQVRUR0NUVEdHVEFDQUNHR0FBQ0dUVENUR0FBQUFHQUdDVEFUR0FBVFRHQ0ENCkdBQ0FDQ1RUVFRHQUFBVFRBQUFUVEdHQ0FBQUdBQUFUVFRHQUNBQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQQ0KVFRUVEdUQVRUVENDQ1RUQUFBVFRDQ0FUQUFUQ0FBR0FDVEFUVENBQUNDQUFHR0dUVEdBQUFBR0FBQUFBDQpHQ1RUR0FUR0dDVFRUQVRHR0dUQUdBQVRUQ0dBVENUR1RDVEFUQ0NBR1RUR0NHVENBQ0NBQUFUR0FBVEcNCkNBQUNDQUFBVEdUR0NDVFRUQ0FBQ1RDVENBVEdBQUdUR1RHQVRDQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQQ0KPk9NNzM5MDUzDQpBQ1RUVENHQVRDVENUVEdUQUdBVENUR1RUQ1RDVEFBQUNHQUFDVFRUQUFBQVRDVEdUR1RHR0NUR1RDQUMNClRDR0dDVEdDQVRHQ1RUQUdUR0NBQ1RDQUNHQ0FHVEFUQUFUVEFBVEFBQ1RBQVRUQUNUR1RDR1RUR0FDQQ0KR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQ1RUQ1RHQ0FHR0NUR0NUVEFDR0dUVFRDR1RDQ0dUR1RUR0NBR0NDDQpHQVRDQVRDQUdDQUNBVENUQUdHVFRUVEdUQ0NHR0dUR1RHQUNDR0FBQUdHVEFBR0FUR0dBR0FHQ0NUVEcNClRDQ0NUR0dUVFRDQUFDR0FHQUFBQUNBQ0FDR1RDQ0FBQ1RDQUdUVFRHQ0NUR1RUVFRBQ0FHR1RUQ0dDRw0KQUNHVEdDVENHVEFDR1RHR0NUVFRHR0FHQUNUQ0NHVEdHQUdHQUdHVENUVEFUQ0FHQUdHQ0FDR1RDQUFDDQpBVENUVEFBQUdBVEdHQ0FDVFRHVEdHQ1RUQUdUQUdBQUdUVEdBQUFBQUdHQ0dUVFRUR0NDVENBQUNUVEcNCkFBQ0FHQ0NDVEFUR1RHVFRDQVRDQUFBQ0dUVENHR0FUR0NUQ0dBQUNUR0NBQ0NUQ0FUR0dUQ0FUR1RUQQ0KVEdHVFRHQUdDVEdHVEFHQ0FHQUFDVENHQUFHR0NBVFRDQUdUQUNHR1RDR1RBR1RHR1RHQUdBQ0FDVFRHDQpHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHQ0dBQUFUQUNDQUdUR0dDVFRBQ0NHQ0FBR0dUVENUVENUVENHVEENCkFHQUFDR0dUQUFUQUFBR0dBR0NUR0dUR0dDQ0FUQUdUVEFDR0dDR0NDR0FUQ1RBQUFHVENBVFRUR0FDVA0KVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQVRDQ1RUQVRHQUFHQVRUVFRDQUFHQUFBQUNUR0dBQUNBQ1RBQUFDDQpBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBQUNUQ0FUR0NHVEdBR0NUVEFBQ0dHQUdHR0dDQVRBQ0FDVENHQ1QNCkFUR1RDR0FUQUFDQUFDVFRDVEdUR0dDQ0NUR0FUR0dDVEFDQ0NUQ1RUR0FHVEdDQVRUQUFBR0FDQ1RUQw0KVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQ0FUR0NBQ1RUVEdUQ0NHQUFDQUFDVEdHQUNUVFRBVFRHQUNBQ1RBDQpBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHVEdBQUNBVEdBR0NBVEdBQUFUVEdDVFRHR1RBQ0FDR0dBQUNHVFQNCkNUR0FBQUFHQUdDVEFUR0FBVFRHQ0FHQUNBQ0NUVFRUR0FBQVRUQUFBVFRHR0NBQUFHQUFBVFRUR0FDQQ0KQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQVRUVFRHVEFUVFRDQ0NUVEFBQVRUQ0NBVEFBVENBQUdBQ1RBVFRDDQpBQUNDQUFHR0dUVEdBQUFBR0FBQUFBR0NUVEdBVEdHQ1RUVEFUR0dHVEFHQUFUVENHQVRDVEdUQ1RBVEMNCkNBR1RUR0NHVENBQ0NBQUFUR0FBVEdDQUFDQ0FBQVRHVEdDQ1RUVENBQUNUQ1RDQVRHQUFHVEdUR0FUQw0KQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQUdBQ0dHR0NHQVRUVFRHVFRBQUFHQ0NBQ1RUR0NHQUFUVFRUR1RHDQo+T1U0NzEwNDANCkFBQ0FBQUNDQUFDQ0FBQ1RUVENHQVRDVENUVEdUQUdBVENUR1RUQ1RDVEFBQUNHQUFDVFRUQUFBQVRDVA0KR1RHVEdHQ1RHVENBQ1RDR0dDVEdDQVRHQ1RUQUdUR0NBQ1RDQUNHQ0FHVEFUQUFUVEFBVEFBQ1RBQVRUDQpBQ1RHVENHVFRHQUNBR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQ1RUQ1RHQ0FHR0NUR0NUVEFDR0dUVFRDR1QNCkNDR1RHVFRHQ0FHQ0NHQVRDQVRDQUdDQUNBVENUQUdHVFRUVEdUQ0NHR0dUR1RHQUNDR0FBQUdHVEFBRw0KQVRHR0FHQUdDQ1RUR1RDQ0NUR0dUVFRDQUFDR0FHQUFBQUNBQ0FDR1RDQ0FBQ1RDQUdUVFRHQ0NUR1RUDQpUVEFDQUdHVFRDR0NHQUNHVEdDVENHVEFDR1RHR0NUVFRHR0FHQUNUQ0NHVEdHQUdHQUdHVENUVEFUQ0ENCkdBR0dDQUNHVENBQUNBVENUVEFBQUdBVEdHQ0FDVFRHVEdHQ1RUQUdUQUdBQUdUVEdBQUFBQUdHQ0dUVA0KVFRHQ0NUQ0FBQ1RUR0FBQ0FHQ0NDVEFUR1RHVFRDQVRDQUFBQ0dUVENHR0FUR0NUQ0dBQUNUR0NBQ0NUDQpDQVRHR1RDQVRHVFRBVEdHVFRHQUdDVEdHVEFHQ0FHQUFDVENHQUFHR0NBVFRDQUdUQUNHR1RDR1RBR1QNCkdHVEdBR0FDQUNUVEdHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHQ0dBQUFUQUNDQUdUR0dDVFRBQ0NHQ0FBRw0KR1RUQ1RUQ1RUQ0dUQUFHQUFDR0dUQUFUQUFBR0dBR0NUR0dUR0dDQ0FUQUdUVEFDR0dDR0NDR0FUQ1RBDQpBQUdUQ0FUVFRHQUNUVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQVRDQ1RUQVRHQUFHQVRUVFRDQUFHQUFBQUMNClRHR0FBQ0FDVEFBQUNBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBQUNUQ0FUR0NHVEdBR0NUVEFBQ0dHQUdHRw0KR0NBVEFDQUNUQ0dDVEFUR1RDR0FUQUFDQUFDVFRDVEdUR0dDQ0NUR0FUR0dDVEFDQ0NUQ1RUR0FHVEdDDQpBVFRBQUFHQUNDVFRDVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQ0FUR0NBQ1RUVEdUQ1RHQUFDQUFDVEdHQUMNClRUVEFUVEdBQ0FDVEFBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHVEdBQUNBVEdBR0NBVEdBQUFUVEdDVFRHRw0KVEFDQUNHR0FBQ0dUVENUR0FBQUFHQUdDVEFUR0FBVFRHQ0FHQUNBQ0NUVFRUR0FBQVRUQUFBVFRHR0NBDQpBQUdBQUFUVFRHQUNBQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQVRUVFRHVEFUVFRDQ0NUVEFBQVRUQ0NBVEENCkFUQ0FBR0FDVEFUVENBQUNDQUFHR0dUVEdBQUFBR0FBQUFBR0NUVEdBVEdHQ1RUVEFUR0dHVEFHQUFUVA0KQ0dBVENUR1RDVEFUQ0NBR1RUR0NHVENBQ0NBQUFUR0FBVEdDQUFDQ0FBQVRHVEdDQ1RUVENBQUNUQ1RDDQpBVEdBQUdUR1RHQVRDQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQUdBQ0dHR0NHQVRUVFRHVFRBQUFHQ0NBQ1Q="

dash.register_page(__name__, path='/getStarted')

ENV_CONFIG = dotenv_values()

NUMBER_OF_COLUMNS_ERROR_MESSAGE = "You need to select at least two columns"
NAME_ERROR_MESSAGE = "You need to give a name to your dataset"

CSV_REGEX = re.compile(r'.*\.csv')
EXCEL_REGEX = re.compile(r'.*\.xls[x]?$')
FASTA_REGEX = re.compile(r'.*\.fasta$')
JSON_REGEX = re.compile(r'.*\.json')

# Load genetic settings from genetic settings file (YAML)
genetic_setting_file = json.load(open('genetic_settings_file.json', 'r'))
Params.update_from_dict(genetic_setting_file)

layout = html.Div([
    dcc.Store(id="ready-for-pipeline", data=False),
    dcc.Store(id='input-data', data={
        'genetic': {'file': None, 'layout': None, 'file_name': None, 'last_modified_date': None, 'type': 'genetic'},
        'climatic': {'file': None, 'layout': None, 'file_name': None, 'last_modified_date': None, 'type': 'climatic'},
        'aligned_genetic': {'file': None, 'layout': None, 'file_name': None, 'last_modified_date': None, 'type': None},
        'genetic_tree': {'file': None, 'file_name': None, 'last_modified_date': None, 'type': None},
        'submit button': False
    }),
    dcc.Store(id='params-climatic', data={'names': None}),
    dcc.Store(id='params-genetic', data={
        'window_size': genetic_setting_file['window_size'],
        'step_size': genetic_setting_file['step_size'],
        'bootstrap_amount': genetic_setting_file['bootstrap_amount'],
        'bootstrap_threshold': genetic_setting_file['bootstrap_threshold'],
        'dist_threshold': genetic_setting_file['dist_threshold'],
        'alignment_method': genetic_setting_file['alignment_method'],
        'distance_method': genetic_setting_file['distance_method'],
        'fit_method': genetic_setting_file['fit_method'],
        'tree_type': genetic_setting_file['tree_type'],
        'rate_similarity': genetic_setting_file['rate_similarity'],
        'method_similarity': genetic_setting_file['method_similarity']
    }),
    html.Div(id='action'),
    html.Div(
        className="get-started",
        children=[
            html.Div(children=[popup.layout]),
            html.Div(children=[popupDone.layout]),
            html.Div(children=[dropFileSection.layout]),
            html.Div([
                html.Div(id="climatic-params-layout"),
                html.Div(id="genetic-params-layout"),
                html.Div(id="submit-button"),
                html.Div([
                    dcc.Input(id='email-input', type='email', placeholder='Enter your email...'),
                    html.Button('Send Email', id='send-email-button')
                ], className='email-container')
            ], id="params-sections")
        ]
    ),
])

@callback(
    Output('send-email-button', 'n_clicks'),
    Input('send-email-button', 'n_clicks'),
    State('email-input', 'value'),
    prevent_initial_call=True
)
def send_email_callback(n_clicks, email):
    if n_clicks > 0 and email:
        subject = 'Your results are on the way!'
        content = 'Your results are ready. Please check the attachment or follow the link to view them.'
        from_email = "iphylogeo@gmail.com"
        from_password = "rogo lqhi fldu mwml"
        send_email(subject, content, email, from_email, from_password)
        return 0  # Reset the button click count to prevent multiple sends
    return n_clicks


@callback(
    Output('params-climatic', 'data'),
    Input('col-analyze', 'value'),
    State('params-climatic', 'data'),
    prevent_initial_call=True
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
    current_data['names'] = column_names
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
@callback (
    Output('upload-climatic-data', 'contents'),
    Output('upload-climatic-data', 'filename'),
    Output('upload-climatic-data', 'children'),
    Input('upload-climatic-data', 'contents'),
    State('upload-climatic-data', 'filename'),
    prevent_initial_call= True
)
def uploaded_climatic_data(climatic_data_contents, climatic_data_filename):
    '''
    This function is called when the user upload climatic data files.
    It displays the name of the file in the upload box.


    Args:
        climatic_data_contents: uploaded climatic data file content in a base64 formatted string.
        climatic_data_filename: name of the uploaded climatic data file
    '''
    # Validate file extension
    if CSV_REGEX.fullmatch(climatic_data_filename) or EXCEL_REGEX.fullmatch(climatic_data_filename):
        return (climatic_data_contents, 
                climatic_data_filename,
                # Output in climatic data upload box
                html.Div(className='loaded-file', children=[
                    html.Img(src='../../assets/icons/folder-drop.svg', className='icon'),
                    html.Div(climatic_data_filename, className='text')]))
    else:
        return (None, 
                None,
                # Output in climatic data upload box
                html.Div(className='loaded-file', children=[
                    html.Img(src='../../assets/icons/folder-drop.svg', className='icon'),
                    html.Div('File must be .csv or Excel', className='text')]))
    

# Callback to show uploaded genetic data files
@callback (
    Output('upload-genetic-data', 'contents'),
    Output('upload-aligned-genetic-data', 'contents'),
    Output('upload-genetic-tree', 'contents'),
    Output('upload-genetic-data', 'filename'),
    Output('upload-aligned-genetic-data', 'filename'),
    Output('upload-genetic-tree', 'filename'),
    Output('upload-genetic-data', 'children'),
    Output('upload-aligned-genetic-data', 'children'),
    Output('upload-genetic-tree', 'children'),
    Input('upload-genetic-data', 'contents'),
    Input('upload-aligned-genetic-data', 'contents'),
    Input('upload-genetic-tree', 'contents'),
    State('upload-genetic-data', 'filename'),
    State('upload-aligned-genetic-data', 'filename'),
    State('upload-genetic-tree', 'filename'),
    prevent_initial_call= True
)
def uploaded_genetic_data(genetic_data_contents, aligned_genetic_data_contents, genetic_tree_contents, genetic_data_filename, aligned_genetic_data_filename, genetic_tree_filename):
    '''
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
    '''
    
    upload_box = dash.callback_context.triggered_id

    if upload_box == 'upload-genetic-data':
        if FASTA_REGEX.fullmatch(genetic_data_filename):
            return (genetic_data_contents,
                    None,
                    None,
                    genetic_data_filename,
                    None,
                    None,
                    # Output in genetic data upload box
                    html.Div(className='loaded-file', children=[
                        html.Img(src='../../assets/icons/folder-drop.svg', className='icon'),
                        html.Div(genetic_data_filename, className='text')]),
                    # Output in aligned genetic data upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload aligned genetic data (.json)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"),
                    # Output in genetic tree upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload genetic tree (.json)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"))
        else:
            return (None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    # Output in genetic data upload box
                    html.Div(className='loaded-file', children=[
                        html.Img(src='../../assets/icons/folder-drop.svg', className='icon'),
                        html.Div('File must be .fasta', className='text')]),
                    # Output in aligned genetic data upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload aligned genetic data (.json)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"),
                    # Output in genetic tree upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload genetic tree (.json)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"))
    elif upload_box == 'upload-aligned-genetic-data':
        if JSON_REGEX.fullmatch(aligned_genetic_data_filename):
            return (None,
                    aligned_genetic_data_contents,
                    None,
                    None,
                    aligned_genetic_data_filename,
                    None,
                    # Output in genetic data upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload genetic data (.fasta)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"),
                    # Output in aligned genetic data upload box
                    html.Div(className='loaded-file', children=[
                        html.Img(src='../../assets/icons/folder-drop.svg', className='icon'),
                        html.Div(aligned_genetic_data_filename, className='text')]),
                    # Output in genetic tree upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload genetic tree (.json)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"))
        else:
            return (None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    # Output in genetic data upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload genetic data (.fasta)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"),
                    # Output in aligned genetic data upload box
                    html.Div(className='loaded-file', children=[
                        html.Img(src='../../assets/icons/folder-drop.svg', className='icon'),
                        html.Div('File must be .json', className='text')]),
                    # Output in genetic tree upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload genetic tree (.json)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"))
    elif upload_box == 'upload-genetic-tree':
        if JSON_REGEX.fullmatch(genetic_tree_filename):
            return (None,
                    None,
                    genetic_tree_contents,
                    None,
                    None,
                    genetic_tree_filename,
                    # Output in genetic data upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload genetic data (.fasta)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"),
                    # Output in aligned genetic data upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload aligned genetic data (.json)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"),
                    # Output in genetic tree upload box
                    html.Div(className='loaded-file', children=[
                        html.Img(src='../../assets/icons/folder-drop.svg', className='icon'),
                        html.Div(genetic_tree_filename, className='text')]))
        else:
            return (None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    # Output in genetic data upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload genetic data (.fasta)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"),
                    # Output in aligned genetic data upload box
                    html.Div([
                        html.A([
                            html.Img(src='../../assets/icons/folder-drop.svg', className="icon"),
                            html.Div('Upload aligned genetic data (.json)', className="text"),
                        ], className="drop-content"),
                    ], className="drop-container", id="drop-container"),
                    # Output in genetic tree upload box
                    html.Div(className='loaded-file', children=[
                        html.Img(src='../../assets/icons/folder-drop.svg', className='icon'),
                        html.Div('File must be .json', className='text')]))
        
@callback(
    Output('genetic-params-layout', 'children'),
    Output('climatic-params-layout', 'children'),
    Output('submit-button', 'children'),
    Output('input-data', 'data'),
    Input('next-button', 'n_clicks'),
    Input('upload-test-data', 'n_clicks'),
    State('upload-genetic-data', 'contents'),
    State('upload-genetic-data', 'filename'),
    State('upload-genetic-data', 'last_modified'),
    State('upload-aligned-genetic-data', 'contents'),
    State('upload-aligned-genetic-data', 'filename'),
    State('upload-aligned-genetic-data', 'last_modified'),
    State('upload-genetic-tree', 'contents'),
    State('upload-genetic-tree', 'filename'),
    State('upload-genetic-tree', 'last_modified'),
    State('upload-climatic-data', 'contents'),
    State('upload-climatic-data', 'filename'),
    State('upload-climatic-data', 'last_modified'),
    State('input-data', 'data'),
    prevent_initial_call=True,
    log=True     
)
def upload_data(next_n_clicks, test_n_clicks, genetic_data_contents, genetic_data_filename, genetic_data_last_modified, aligned_genetic_data_contents, aligned_genetic_data_filename, aligned_genetic_data_last_modified, genetic_tree_contents, genetic_tree_filename, genetic_tree_last_modified, climatic_data_contents, climatic_data_filename, climatic_data_last_modified, current_data):
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
    genetic_data_is_present = genetic_data_contents is not None and genetic_data_contents != ''
    aligned_genetic_data_is_present = aligned_genetic_data_contents is not None and aligned_genetic_data_contents != ''
    genetic_tree_is_present = genetic_tree_contents is not None and genetic_tree_contents != ''
    climatic_data_is_present = climatic_data_contents is not None and climatic_data_contents != ''
    climatic_data_to_show = False
    genetic_data_to_show = False
    climatic_data_is_missing = not climatic_data_is_present
    genetic_data_is_missing = not genetic_data_is_present and not aligned_genetic_data_is_present and  not genetic_tree_is_present

    button_clicked = ctx.triggered_id

    if button_clicked == "next-button" and (climatic_data_is_missing or genetic_data_is_missing):
            raise PreventUpdate
    
    submit_button = None
    if not current_data['submit button']:
        current_data['submit button'] = True
        submit_button = submitButton.layout

    if button_clicked == 'upload-test-data':
        # Test data example "Don't know where to start?"
        # Show graph for genetic data
        parsed_genetic_file = parse_uploaded_files(CONTENT_GENETIC, 'seq very small.fasta')
        current_data['genetic']['file'] = parsed_genetic_file['dataframe'] #dict key=  value= fasta strings
        current_data['genetic']['layout'] = paramsGenetic.get_layout(parsed_genetic_file['dataframe'])
        current_data['genetic']['file_name'] = 'seq very small.fasta'
        current_data['genetic']['last_modified_date'] = 1680370585.9890237
        genetic_data_to_show = True
        # Change aligned genetic data and genetic tree to None
        current_data['aligned_genetic']['file'] = None
        current_data['aligned_genetic']['file_name'] = None
        current_data['aligned_genetic']['last_modified_date'] = None
        current_data['aligned_genetic']['file_name'] = None
        current_data['genetic_tree']['file'] = None
        current_data['genetic_tree']['file_name'] = None
        current_data['genetic_tree']['last_modified_date'] = None
        # Show graph for climatic data
        # Show graphs, table and columns to choose 
        parsed_climatic_file = parse_uploaded_files(CONTENT_CLIMATIC, 'geo.csv')
        current_data['climatic']['file'] = parsed_climatic_file['dataframe'].to_json() #json of a pandas dataframe
        current_data['climatic']['layout'] = paramsClimatic.create_table(parsed_climatic_file['dataframe'])
        current_data['climatic']['file_name'] = 'geo.csv'
        current_data['climatic']['last_modified_date'] = 1680370585.9880235
        climatic_data_to_show = True
    
    elif button_clicked == 'next-button':
        if genetic_data_is_present:
            # Show graph
            parsed_genetic_file = parse_uploaded_files(genetic_data_contents, genetic_data_filename)
            current_data['genetic']['file'] = parsed_genetic_file['dataframe'] #dict key=  value= fasta strings
            current_data['genetic']['layout'] = paramsGenetic.get_layout(parsed_genetic_file['dataframe'])
            current_data['genetic']['file_name'] = genetic_data_filename
            current_data['genetic']['last_modified_date'] = genetic_data_last_modified
            genetic_data_to_show = True
            # Change aligned genetic data and genetic tree to None
            current_data['aligned_genetic']['file'] = None
            current_data['aligned_genetic']['file_name'] = None
            current_data['aligned_genetic']['last_modified_date'] = None
            current_data['genetic_tree']['file'] = None
            current_data['genetic_tree']['file_name'] = None
            current_data['genetic_tree']['last_modified_date'] = None
        elif aligned_genetic_data_is_present:
            # Won't show any graphs
            parsed_aligned_genetic_file = parse_uploaded_files(aligned_genetic_data_contents, aligned_genetic_data_filename)
            current_data['aligned_genetic']['file'] = parsed_aligned_genetic_file['dataframe'] # json object 
            current_data['aligned_genetic']['file_name'] = aligned_genetic_data_filename
            current_data['aligned_genetic']['last_modified_date'] = aligned_genetic_data_last_modified
            genetic_data_to_show: False
            # Change genetic data and genetic tree to None
            current_data['genetic']['file'] = None
            current_data['genetic']['layout'] = None
            current_data['genetic']['file_name'] = None
            current_data['genetic']['last_modified_date'] = None
            current_data['genetic_tree']['file'] = None
            current_data['genetic_tree']['file_name'] = None
            current_data['genetic_tree']['last_modified_date'] = None
        elif genetic_tree_is_present:
            # Won't show any graphs
            parsed_genetic_tree_file = parse_uploaded_files(genetic_tree_contents, genetic_tree_filename)
            current_data['genetic_tree']['file'] = parsed_genetic_tree_file['dataframe'] #json object
            current_data['genetic_tree']['file_name'] = genetic_tree_filename
            current_data['genetic_tree']['last_modified_date'] = genetic_tree_last_modified
            genetic_data_to_show: False
            # Change aligned genetic data and genetic data to None
            current_data['genetic']['file'] = None
            current_data['genetic']['layout'] = None
            current_data['genetic']['file_name'] = None
            current_data['genetic']['last_modified_date'] = None
            current_data['aligned_genetic']['file'] = None
            current_data['aligned_genetic']['file_name'] = None
            current_data['aligned_genetic']['last_modified_date'] = None
        
        if climatic_data_is_present:
            # Show graphs, table and columns to choose 
            parsed_climatic_file = parse_uploaded_files(climatic_data_contents, climatic_data_filename)
            current_data['climatic']['file'] = parsed_climatic_file['dataframe'].to_json() #json of a pandas dataframe
            current_data['climatic']['layout'] = paramsClimatic.create_table(parsed_climatic_file['dataframe'])
            current_data['climatic']['file_name'] = climatic_data_filename
            current_data['climatic']['last_modified_date'] = climatic_data_last_modified
            climatic_data_to_show = True

    
    if climatic_data_to_show and genetic_data_to_show:
        return current_data['genetic']['layout'], current_data['climatic']['layout'], submit_button, current_data
    elif climatic_data_to_show:
        return '', current_data['climatic']['layout'], submit_button, current_data
    elif genetic_data_to_show:
        return current_data['genetic']['layout'], '', submit_button, current_data
    else:
        return '', '', submit_button, current_data
    
def parse_uploaded_files(content, file_name):
    """
    Parse a base64 string into the proper format to pass through the aPhyloGeo pipeline

    Args:
        content (base64 string): uploaded content from Dash Upload Module
        file_name (string): file name

    """
    results = {}

    try:
        content_type, content_string = content.split(',')
        decoded_content = base64.b64decode(content_string)

        if content_type == 'data:text/csv;base64' or content_type == 'data:application/vnd.ms-excel;base64':
            # Assume that the user uploaded a CSV file (climatic data)
            results['type'] = 'csv'
            results['dataframe'] = pd.read_csv(io.StringIO(decoded_content.decode('utf-8')))
        elif EXCEL_REGEX.fullmatch(file_name):
            # Assume that the user uploaded an excel f 
            # ile (climatic data)
            results['type'] = 'excel'
            results['dataframe'] = pd.read_excel(io.BytesIO(decoded_content))
        elif FASTA_REGEX.fullmatch(file_name):
            # Assume that the user uploaded a fasta file (genetic data)
            fasta_file_string = decoded_content.decode('utf-8')
            results['type'] = 'fasta'
            results['dataframe'] = files_ctrl.fasta_to_str(SeqIO.parse(io.StringIO(fasta_file_string), 'fasta'))
            # Save the fasta file (needed for aPhyloGeo Alignment)
            with open('./temp/genetic_data.fasta', 'w') as f:
                f.write(fasta_file_string.replace("\r\n", '\n'))
        elif content_type == 'data:application/json;base64':
            # Assume  that the user uploaded a JSON file (aligned genetic data)
            results['type'] = 'json'
            results['dataframe'] = decoded_content.decode('utf-8')

        results['base64'] = content_string

        return results
        
    except Exception as e:
        print(e)

@callback(
    Output('popup', 'className'),
    Output('column-error-message', 'children'),
    Output('name-error-message', 'children'),
    Output('ready-for-pipeline', 'data'),
    [Input('submit-dataset', 'n_clicks'),
    # Input("close_popup", "n_clicks"),
    Input('input-dataset', 'value')],
    State('input-data', 'data'),
    State('params-climatic', 'data'),
    prevent_initial_call=True
)
def ready_for_pipeline(open, result_name, input_data, params_climatic):
    """
    Verify the following prerequisites needed for aPhyloGeo pipeline to start:
     - At least two columns are selected from the climatic data file.
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
    # Add climatic column names to Params
    if params_climatic['names'] is not None:
        names = ['id'] + params_climatic['names']
        params_climatic['names'] = names
        Params.names = names

    # Assure there is at least one genetic file and one climatic file uploaded
    files_are_present = ((input_data['genetic']['file'] is not None or
                          input_data['aligned_genetic']['file'] is not None or
                          input_data['genetic_tree']['file'] is not None)
                          and
                          (input_data['climatic']['file'] is not None))
    
    climatic_data_is_present = input_data['climatic']['file'] is not None

    if open is None or open < 1 or not files_are_present:
        raise PreventUpdate

    trigger_id = ctx.triggered_id

    # if trigger_id == "close_popup":
    #     return 'popup hidden', '', '', False

    # Assure there is a dataset name given by the user
    result_name_is_valid = result_name is not None and result_name != ''
    params_climatic_is_complete = params_climatic['names'] is not None and len(params_climatic['names']) >= 2

    # Assure that at least two columns from the climatic data are selected
    if climatic_data_is_present and not params_climatic_is_complete and result_name_is_valid:
        return 'popup hidden', dbc.Alert(NUMBER_OF_COLUMNS_ERROR_MESSAGE, color="danger"), '', False
    elif climatic_data_is_present and params_climatic_is_complete and not result_name_is_valid:
        return 'popup hidden', '', dbc.Alert(NAME_ERROR_MESSAGE, color="danger"), False
    elif climatic_data_is_present and not params_climatic_is_complete and not result_name_is_valid:
        return 'popup hidden', dbc.Alert(NUMBER_OF_COLUMNS_ERROR_MESSAGE, color="danger"), dbc.Alert(NAME_ERROR_MESSAGE, color="danger"), False

    if trigger_id != "submit-dataset":
        return '', '', '', False
    
    return 'popup', '', '', True

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, content, user_email, from_email, from_password):
    try:
        # Crear el mensaje
        message = MIMEMultipart("alternative")
        message["From"] = from_email
        message["To"] = user_email
        message["Subject"] = subject
        
        # Cuerpo del mensaje en HTML
        html_content = MIMEText(content, "html", "UTF-8")
        message.attach(html_content)

        my_message = message.as_string()
        
        # Establecer conexión con el servidor SMTP
        email_session = smtplib.SMTP('smtp.gmail.com', 587)
        email_session.starttls()
        email_session.login(from_email, from_password)
        email_session.sendmail(from_email, user_email, my_message)
        email_session.quit()
        print("Email was sent successfully.")
    except Exception as e:
        print(f"Error: {e}")
        print("Unable to send email")

@callback(
    Output('popupDone', 'className'),
    Input('ready-for-pipeline', 'data'),
    State('input-data', 'data'),
    State('params-climatic', 'data'),
    State('params-genetic', 'data'),
    State('input-dataset', 'value'),
    State('email-input', 'value'),
    prevent_initial_call=True
)
def submit_button(ready_for_pipeline, input_data, params_climatic, params_genetic, result_name, email):
    if ready_for_pipeline is False:
        return 'popup hidden'

    climatic_file = input_data['climatic']['file']

    genetic_file = input_data['genetic']['file']
    aligned_genetic_file = input_data['aligned_genetic']['file']
    genetic_tree_file = input_data['genetic_tree']['file']
    
    result_type = []
    files_ids = {}
    if climatic_file is not None:
        result_type.append('climatic')
        climatic_file_id = utils.save_files(input_data['climatic'])
        files_ids['climatic_files_id'] = climatic_file_id

    if genetic_file is not None:
        result_type.append('genetic')
        genetic_file_id = utils.save_files(input_data['genetic'])
        files_ids['genetic_files_id'] = genetic_file_id

    if aligned_genetic_file is not None:
        result_type.append('genetic')
        aligned_genetic_file_id = utils.save_files(input_data['aligned_genetic'])
        files_ids['aligned_genetic_files_id'] = aligned_genetic_file_id

    if genetic_tree_file is not None:
        result_type.append('genetic')
        genetic_tree_file_id = utils.save_files(input_data['genetic_tree'])
        files_ids['genetic_tree_files_id'] = genetic_tree_file_id

    try:
        # create a new result in the database
        result_id = utils.create_result(files_ids, result_type, params_climatic, params_genetic, result_name)
        if ENV_CONFIG['HOST'] != 'local':
            add_result_to_cookie(result_id)
        
        # Prepare climatic trees
        climatic_trees = utils.create_climatic_trees(result_id, climatic_file)
        
        genetic_trees = None

        # Prepare genetic trees
        if genetic_file is not None:
            reference_gene_file = {
                "reference_gene_dir": os.getcwd() + "\\temp",
                "reference_gene_file": "genetic_data.fasta"
            }
            Params.update_from_dict(reference_gene_file)

            utils.run_genetic_pipeline(result_id, climatic_file, genetic_file, climatic_trees) 
        elif aligned_genetic_file is not None:
            
            loaded_seq_alignment = Alignment.from_json_string(aligned_genetic_file)
            msaSet = loaded_seq_alignment.msa
            
            results_ctrl.update_result({
            '_id': result_id,
            'msaSet': msaSet,
            'status': 'alignment'})

            genetic_trees = utils.create_genetic_trees(result_id, msaSet)
            utils.create_output(result_id, climatic_trees, genetic_trees, pd.read_json(io.StringIO(climatic_file)))
        elif genetic_tree_file is not None: 

            loaded_genetic_trees = GeneticTrees.load_trees_from_json(genetic_tree_file)
            genetic_trees = loaded_genetic_trees.trees 

            results_ctrl.update_result({
            '_id': result_id,
            'genetic_trees': genetic_trees,
            'status': "genetic_trees"
            })

            utils.create_output(result_id, climatic_trees, genetic_trees, pd.read_json(io.StringIO(climatic_file)))

        # Enviar el correo cuando los resultados estén listos
        if email:
            subject = 'Your results are ready'
            content = f'Your results are now ready. You can view them at the following link: '
            send_email(subject, content, email, "iphylogeo@gmail.com", "rogo lqhi fldu mwml")

        return 'popup'
    except Exception as e:
        print('[Error]:', e)
        return 'popup'