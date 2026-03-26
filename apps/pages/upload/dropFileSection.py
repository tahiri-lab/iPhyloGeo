from dash import ClientsideFunction, Input, Output, State, callback, clientside_callback, ctx, dcc, html
from components.badge import create_badge
from utils.i18n import t

# this is a shortcut. It's the base64 content of the test files (geo.csv and genetic.csv)
# TODO: find a way to load the files from the server and use them instead
CONTENT_CLIMATIC = "data:text/csv;base64,aWQsQUxMU0tZX1NGQ19TV19EV04sVDJNLFFWMk0sUFJFQ1RPVENPUlIsV1MxME0NCk9NNzM5MDUzLDQuNywxNC44MDMzMzMzMzMzMzMzMzUsNi43MTMzMzMzMzMzMzMzMzQsMS42MjMzMzMzMzMzMzMzMzMsMi41NTMzMzMzMzMzMzMzMzMyDQpPVTQ3MTA0MCwxLjQ2LDQuMTksNC41MTY2NjY2NjY2NjY2NjcsMC4xMiwzLjA0MzMzMzMzMzMzMzMzMw0KT04xMjk0MjksNi44OTMzMzMzMzMzMzMzMzM1LDI3LjA2NjY2NjY2NjY2NjY2NiwxNS4xNTY2NjY2NjY2NjY2NjUsMC43MTY2NjY2NjY2NjY2NjY3LDEuMzYNCk9MOTg5MDc0LDQuNjQ2NjY2NjY2NjY2NjY2NSwyNi4xMiwxOC4xMDY2NjY2NjY2NjY2NzYsMC40NzMzMzMzMzMzMzMzMzM0LDUuNjYNCk9OMTM0ODUyLDYuODQwMDAwMDAwMDAwMDAyNSwxNi45NzMzMzMzMzMzMzMzMzMsNS41NzY2NjY2NjY2NjY2NjcsMC40OTY2NjY2NjY2NjY2NjY2LDQuNjY2NjY2NjY2NjY2NjY3"
CONTENT_GENETIC = "data:application/octet-stream;base64,Pk9OMTI5NDI5DQpBQ1RUVENHQVRDVENUVEdUQUdBVENUR1RUQ1RDVEFBQUNHQUFDVFRUQUFBQVRDVEdUR1RHR0NUR1RDQUMNClRDR0dDVEdDQVRHQ1RUQUdUR0NBQ1RDQUNHQ0FHVEFUQUFUVEFBVEFBQ1RBQVRUQUNUR1RDR1RUR0FDQQ0KR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQ1RUQ1RHQ0FHR0NUR0NUVEFDR0dUVFRDR1RDQ0dUR1RUR0NBR0NDDQpHQVRDQVRDQUdDQUNBVENUQUdHVFRUVEdUQ0NHR0dUR1RHQUNDR0FBQUdHVEFBR0FUR0dBR0FHQ0NUVEcNClRDQ0NUR0dUVFRDQUFDR0FHQUFBQUNBQ0FDR1RDQ0FBQ1RDQUdUVFRHQ0NUR1RUVFRBQ0FHR1RUQ0dDRw0KQUNHVEdDVENHVEFDR1RHR0NUVFRHR0FHQUNUQ0NHVEdHQUdHQUdHVENUVEFUQ0FHQUdHQ0FDR1RDQUFDDQpBVENUVEFBQUdBVEdHQ0FDVFRHVEdHQ1RUQUdUQUdBQUdUVEdBQUFBQUdHQ0dUVFRUR0NDVENBQUNUVEcNCkFBQ0FHQ0NDVEFUR1RHVFRDQVRDQUFBQ0dUVENHR0FUR0NUQ0dBQUNUR0NBQ0NUQ0FUR0dUQ0FUR1RUQQ0KVEdHVFRHQVRDVEdHVEFHQ0FHQUFDVENHQUFHR0NBVFRDQUdUQUNHR1RDR1RBR1RHR1RHQUdBQ0FDVFRHDQpHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHQ0dBQUFUQUNDQUdUR0dDVFRBQ0NHQ0FBR0dUVENUVENUVENHVEENCkFHQUFDR0dUQUFUQUFBR0dBR0NUR0dUR0dDQ0FUQUdUVEFDR0dDR0NDR0FUQ1RBQUFHVENBVFRUR0FDVA0KVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQVRDQ1RUQVRHQUFHQVRUVFRDQUFHQUFBQUNUR0dBQUNBQ1RBQUFDDQpBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBQUNUQ0FUR0NHVEdBR0NUVEFBQ0dHQUdHR0dDQVRBQ0FDVENHQ1QNCkFUR1RDR0FUQUFDQUFDVFRDVEdUR0dDQ0NUR0FUR0dDVEFDQ0NUQ1RUR0FHVEdDQVRUQUFBR0FDQ1RUQw0KVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQ0FUR0NBQ1RUVEdUQ1RHQUFDQUFDVEdHQUNUVFRBVFRHQUNBQ1RBDQpBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHVEdBQUNBVEdBR0NBVEdBQUFUVEdDVFRHR1RBQ0FDR0dBQUNHVFQNCkNUR0FBQUFHQUdDVEFUR0FBVFRHQ0FHQUNBQ0NUVFRUR0FBQVRUQUFBVFRHR0NBQUFHQUFBVFRUR0FDQQ0KQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQVRUVFRHVEFUVFRDQ0NUVEFBQVRUQ0NBVEFBVENBQUdBQ1RBVFRDDQpBQUNDQUFHR0dUVEdBQUFBR0FBQUFBR0NUVEdBVEdHQ1RUVEFUR0dHVEFHQUFUVENHQVRDVEdUQ1RBVEMNCkNBR1RUR0NHVENBQ0NBQUFUR0FBVEdDQUFDQ0FBQVRHVEdDQ1RUVENBQUNUQ1RDQVRHQUFHVEdUR0FUQw0KQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQUdBQ0dHR0NHQVRUVFRHVFRBQUFHQ0NBQ1RUR0NHQUFUVFRUR1RHDQo+T04xMzQ4NTINCkFHQVRDVEdUVENUQ1RBQUFDR0FBQ1RUVEFBQUFUQ1RHVEdUR0dDVEdUQ0FDVENHR0NUR0NBVEdDVFRBRw0KVEdDQUNUQ0FDR0NBR1RBVEFBVFRBQVRBQUNUQUFUVEFDVEdUQ0dUVEdBQ0FHR0FDQUNHQUdUQUFDVENHDQpUQ1RBVENUVENUR0NBR0dDVEdDVFRBQ0dHVFRUQ0dUQ0NHVEdUVEdDQUdDQ0dBVENBVENBR0NBQ0FUQ1QNCkFHR1RUVFRHVENDR0dHVEdUR0FDQ0dBQUFHR1RBQUdBVEdHQUdBR0NDVFRHVENDQ1RHR1RUVENBQUNHQQ0KR0FBQUFDQUNBQ0dUQ0NBQUNUQ0FHVFRUR0NDVEdUVFRUQUNBR0dUVENHQ0dBQ0dUR0NUQ0dUQUNHVEdHDQpDVFRUR0dBR0FDVENDR1RHR0FHR0FHR1RDVFRBVENBR0FHR0NBQ0dUQ0FBQ0FUQ1RUQUFBR0FUR0dDQUMNClRUR1RHR0NUVEFHVEFHQUFHVFRHQUFBQUFHR0NHVFRUVEdDQ1RDQUFDVFRHQUFDQUdDQ0NUQVRHVEdUVA0KQ0FUQ0FBQUNHVFRDR0dBVEdDVENHQUFDVEdDQUNDVENBVEdHVENBVEdUVEFUR0dUVEdBR0NUR0dUQUdDDQpBR0FBQ1RDR0FBR0dDQVRUQ0FHVEFDR0dUQ0dUQUdUR0dUR0FHQUNBQ1RUR0dUR1RDQ1RUR1RDQ0NUQ0ENClRHVEdHR0NHQUFBVEFDQ0FHVEdHQ1RUQUNDR0NBQUdHVFRDVFRDVFRDR1RBQUdBQUNHR1RBQVRBQUFHRw0KQUdDVEdHVEdHQ0NBVEFHVFRBQ0dHQ0dDQ0dBVENUQUFBR1RDQVRUVEdBQ1RUQUdHQ0dBQ0dBR0NUVEdHDQpDQUNUR0FUQ0NUVEFUR0FBR0FUVFRUQ0FBR0FBQUFDVEdHQUFDQUNUQUFBQ0FUQUdDQUdUR0dUR1RUQUMNCkNDR1RHQUFDVENBVEdDR1RHQUdDVFRBQUNHR0FHR0dHQ0FUQUNBQ1RDR0NUQVRHVENHQVRBQUNBQUNUVA0KQ1RHVEdHQ0NDVEdBVEdHQ1RBQ0NDVENUVEdBR1RHQ0FUVEFBQUdBQ0NUVENUQUdDQUNHVEdDVEdHVEFBDQpBR0NUVENBVEdDQUNUVFRHVENDR0FBQ0FBQ1RHR0FDVFRUQVRUR0FDQUNUQUFHQUdHR0dUR1RBVEFDVEcNCkNUR0NDR1RHQUFDQVRHQUdDQVRHQUFBVFRHQ1RUR0dUQUNBQ0dHQUFDR1RUQ1RHQUFBQUdBR0NUQVRHQQ0KQVRUR0NBR0FDQUNDVFRUVEdBQUFUVEFBQVRUR0dDQUFBR0FBQVRUVEdBQ0FDQ1RUQ0FBVEdHR0dBQVRHDQpUQ0NBQUFUVFRUR1RBVFRUQ0NDVFRBQUFUVENDQVRBQVRDQUFHQUNUQVRUQ0FBQ0NBQUdHR1RUR0FBQUENCkdBQUFBQUdDVFRHQVRHR0NUVFRBVEdHR1RBR0FBVFRDR0FUQ1RHVENUQVRDQ0FHVFRHQ0dUQ0FDQ0FBQQ0KVEdBQVRHQ0FBQ0NBQUFUR1RHQ0NUVFRDQUFDVENUQ0FUR0FBR1RHVEdBVENBVFRHVEdHVEdBQUFDVFRDDQpBVEdHQ0FHQUNHR0dDR0FUVFRUR1RUQUFBR0NDQUNUVEdDR0FBVFRUVEdUR0dDQUNUR0FHQUFUVFRHQUMNClQNCj5PTDk4OTA3NA0KQVRUQUFBR0dUVFRBVEFDQ1RUQ0NDQUdHVEFBQ0FBQUNDQUFDQ0FBQ1RUVENHQVRDVENUVEdUQUdBVENUDQpHVFRDVFRUQUFBQ0dBQUNUVFRBQUFBVENUR1RHVEdHQ1RHVENBQ1RDR0dDVEdDQVRHQ1RUQUdUR0NBQ1QNCkNBQ0dDQUdUQVRBQVRUQUFUQUFDVEFBVFRBQ1RHVENHVFRHQUNBR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQw0KVFRDVEdDQUdHQ1RHQ1RUQUNHR1RUVENHVENDR1RHVFRHQ0FHQ0NHQVRDQVRDQUdDQUNBVENUQUdHVFRUDQpUR1RDQ0dHR1RHVEdBQ0NHQUFBR0dUQUFHQVRHR0FHQUdDQ1RUR1RDQ0NUR0dUVFRDQUFDR0FHQUFBQUMNCkFDQUNHVENDQUFDVENBR1RUVEdDQ1RHVFRUVEFDQUdHVFRDR0NHQUNHVEdDVENHVEFDR1RHR0NUVFRHRw0KQUdBQ1RDQ0dUR0dBR0dBR0dUQ1RUQVRDQUdBR0dDQUNHVENBQUNBVENUVEFBQUdBVEdHQ0FDVFRHVEdHDQpDVFRBR1RBR0FBR1RUR0FBQUFBR0dDR1RUVFRHQ0NUQ0FBQ1RUR0FBQ0FHQ0NDVEFUR1RHVFRDQVRDQUENCkFDR1RUQ0dHQVRHQ1RDR0FBQ1RHQ0FDQ1RDQVRHR1RDQVRHVFRBVEdHVFRHQUdDVEdHVEFHQ0FHQUFDVA0KQ0dBQUdHQ0FUVENBR1RBQ0dHVENHVEFHVEdHVEdBR0FDQUNUVEdHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHDQpDR0FBQVRBQ0NBR1RHR0NUVEFDQ0dDQUFHR1RUQ1RUQ1RUQ0dUQUFHQUFDR0dUQUFUQUFBR0dBR0NUR0cNClRHR0NDQVRBR1RUQUNHR0NHQ0NHQVRDVEFOTk5OTk5OTk5HQUNUVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQQ0KVENDVFRBVEdBQUdBVFRUVENBQUdBQUFBQ1RHR0FBQ0FDVEFBQUNBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBDQpBQ1RDQVRHQ0dUR0FHQ1RUQUFDR0dBR0dHR0NBVEFDQUNUQ0dDVEFUR1RDR0FUQUFDQUFDVFRDVEdUR0cNCkNDQ1RHQVRHR0NUQUNDQ1RDVFRHQUdUR0NBVFRBQUFHQUNDVFRDVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQw0KQVRHQ0FDVFRUR1RDQ0dBQUNBQUNUR0dBQ1RUVEFUVEdBQ0FDVEFBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHDQpUR0FBQ0FUR0FHQ0FUR0FBQVRUR0NUVEdHVEFDQUNHR0FBQ0dUVENUR0FBQUFHQUdDVEFUR0FBVFRHQ0ENCkdBQ0FDQ1RUVFRHQUFBVFRBQUFUVEdHQ0FBQUdBQUFUVFRHQUNBQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQQ0KVFRUVEdUQVRUVENDQ1RUQUFBVFRDQ0FUQUFUQ0FBR0FDVEFUVENBQUNDQUFHR0dUVEdBQUFBR0FBQUFBDQpHQ1RUR0FUR0dDVFRUQVRHR0dUQUdBQVRUQ0dBVENUR1RDVEFUQ0NBR1RUR0NHVENBQ0NBQUFUR0FBVEcNCkNBQUNDQUFBVEdUR0NDVFRUQ0FBQ1RDVENBVEdBQUdUR1RHQVRDQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQQ0KPk9NNzM5MDUzDQpBQ1RUVENHQVRDVENUVEdUQUdBVENUR1RUQ1RDVEFBQUNHQUFDVFRUQUFBQVRDVEdUR1RHR0NUR1RDQUMNClRDR0dDVEdDQVRHQ1RUQUdUR0NBQ1RDQUNHQ0FHVEFUQUFUVEFBVEFBQ1RBQVRUQUNUR1RDR1RUR0FDQQ0KR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQ1RUQ1RHQ0FHR0NUR0NUVEFDR0dUVFRDR1RDQ0dUR1RUR0NBR0NDDQpHQVRDQVRDQUdDQUNBVENUQUdHVFRUVEdUQ0NHR0dUR1RHQUNDR0FBQUdHVEFBR0FUR0dBR0FHQ0NUVEcNClRDQ0NUR0dUVFRDQUFDR0FHQUFBQUNBQ0FDR1RDQ0FBQ1RDQUdUVFRHQ0NUR1RUVFRBQ0FHR1RUQ0dDRw0KQUNHVEdDVENHVEFDR1RHR0NUVFRHR0FHQUNUQ0NHVEdHQUdHQUdHVENUVEFUQ0FHQUdHQ0FDR1RDQUFDDQpBVENUVEFBQUdBVEdHQ0FDVFRHVEdHQ1RUQUdUQUdBQUdUVEdBQUFBQUdHQ0dUVFRUR0NDVENBQUNUVEcNCkFBQ0FHQ0NDVEFUR1RHVFRDQVRDQUFBQ0dUVENHR0FUR0NUQ0dBQUNUR0NBQ0NUQ0FUR0dUQ0FUR1RUQQ0KVEdHVFRHQVRDVEdHVEFHQ0FHQUFDVENHQUFHR0NBVFRDQUdUQUNHR1RDR1RBR1RHR1RHQUdBQ0FDVFRHDQpHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHQ0dBQUFUQUNDQUdUR0dDVFRBQ0NHQ0FBR0dUVENUVENUVENHVEENCkFHQUFDR0dUQUFUQUFBR0dBR0NUR0dUR0dDQ0FUQUdUVEFDR0dDR0NDR0FUQ1RBQUFHVENBVFRUR0FDVA0KVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQVRDQ1RUQVRHQUFHQVRUVFRDQUFHQUFBQUNUR0dBQUNBQ1RBQUFDDQpBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBQUNUQ0FUR0NHVEdBR0NUVEFBQ0dHQUdHR0dDQVRBQ0FDVENHQ1QNCkFUR1RDR0FUQUFDQUFDVFRDVEdUR0dDQ0NUR0FUR0dDVEFDQ0NUQ1RUR0FHVEdDQVRUQUFBR0FDQ1RUQw0KVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQ0FUR0NBQ1RUVEdUQ1RHQUFDQUFDVEdHQUNUVFRBVFRHQUNBQ1RBDQpBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHVEdBQUNBVEdBR0NBVEdBQUFUVEdDVFRHR1RBQ0FDR0dBQUNHVFQNCkNUR0FBQUFHQUdDVEFUR0FBVFRHQ0FHQUNBQ0NUVFRUR0FBQVRUQUFBVFRHR0NBQUFHQUFBVFRUR0FDQQ0KQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQVRUVFRHVEFUVFRDQ0NUVEFBQVRUQ0NBVEFBVENBQUdBQ1RBVFRDDQpBQUNDQUFHR0dUVEdBQUFBR0FBQUFBR0NUVEdBVEdHQ1RUVEFUR0dHVEFHQUFUVENHQVRDVEdUQ1RBVEMNCkNBR1RUR0NHVENBQ0NBQUFUR0FBVEdDQUFDQ0FBQVRHVEdDQ1RUVENBQUNUQ1RDQVRHQUFHVEdUR0FUQw0KQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQUdBQ0dHR0NHQVRUVFRHVFRBQUFHQ0NBQ1RUR0NHQUFUVFRUR1RHDQo+T1U0NzEwNDANCkFBQ0FBQUNDQUFDQ0FBQ1RUVENHQVRDVENUVEdUQUdBVENUR1RUQ1RDVEFBQUNHQUFDVFRUQUFBQVRDVA0KR1RHVEdHQ1RHVENBQ1RDR0dDVEdDQVRHQ1RUQUdUR0NBQ1RDQUNHQ0FHVEFUQUFUVEFBVEFBQ1RBQVRUDQpBQ1RHVENHVFRHQUNBR0dBQ0FDR0FHVEFBQ1RDR1RDVEFUQ1RUQ1RHQ0FHR0NUR0NUVEFDR0dUVFRDR1QNCkNDR1RHVFRHQ0FHQ0NHQVRDQVRDQUdDQUNBVENUQUdHVFRUVEdUQ0NHR0dUR1RHQUNDR0FBQUdHVEFBRw0KQVRHR0FHQUdDQ1RUR1RDQ0NUR0dUVFRDQUFDR0FHQUFBQUNBQ0FDR1RDQ0FBQ1RDQUdUVFRHQ0NUR1RUDQpUVEFDQUdHVFRDR0NHQUNHVEdDVENHVEFDR1RHR0NUVFRHR0FHQUNUQ0NHVEdHQUdHQUdHVENUVEFUQ0ENCkdBR0dDQUNHVENBQUNBVENUVEFBQUdBVEdHQ0FDVFRHVEdHQ1RUQUdUQUdBQUdUVEdBQUFBQUdHQ0dUVA0KVFRHQ0NUQ0FBQ1RUR0FBQ0FHQ0NDVEFUR1RHVFRDQVRDQUFBQ0dUVENHR0FUR0NUQ0dBQUNUR0NBQ0NUDQpDQVRHR1RDQVRHVFRBVEdHVFRHQUdDVEdHVEFHQ0FHQUFDVENHQUFHR0NBVFRDQUdUQUNHR1RDR1RBR1QNCkdHVEdBR0FDQUNUVEdHVEdUQ0NUVEdUQ0NDVENBVEdUR0dHQ0dBQUFUQUNDQUdUR0dDVFRBQ0NHQ0FBRw0KR1RUQ1RUQ1RUQ0dUQUFHQUFDR0dUQUFUQUFBR0dBR0NUR0dUR0dDQ0FUQUdUVEFDR0dDR0NDR0FUQ1RBDQpBQUdUQ0FUVFRHQUNUVEFHR0NHQUNHQUdDVFRHR0NBQ1RHQVRDQ1RUQVRHQUFHQVRUVFRDQUFHQUFBQUMNClRHR0FBQ0FDVEFBQUNBVEFHQ0FHVEdHVEdUVEFDQ0NHVEdBQUNUQ0FUR0NHVEdBR0NUVEFBQ0dHQUdHRw0KR0NBVEFDQUNUQ0dDVEFUR1RDR0FUQUFDQUFDVFRDVEdUR0dDQ0NUR0FUR0dDVEFDQ0NUQ1RUR0FHVEdDDQpBVFRBQUFHQUNDVFRDVEFHQ0FDR1RHQ1RHR1RBQUFHQ1RUQ0FUR0NBQ1RUVEdUQ1RHQUFDQUFDVEdHQUMNClRUVEFUVEdBQ0FDVEFBR0FHR0dHVEdUQVRBQ1RHQ1RHQ0NHVEdBQUNBVEdBR0NBVEdBQUFUVEdDVFRHRw0KVEFDQUNHR0FBQ0dUVENUR0FBQUFHQUdDVEFUR0FBVFRHQ0FHQUNBQ0NUVFRUR0FBQVRUQUFBVFRHR0NBDQpBQUdBQUFUVFRHQUNBQ0NUVENBQVRHR0dHQUFUR1RDQ0FBQVRUVFRHVEFUVFRDQ0NUVEFBQVRUQ0NBVEENCkFUQ0FBR0FDVEFUVENBQUNDQUFHR0dUVEdBQUFBR0FBQUFBR0NUVEdBVEdHQ1RUVEFUR0dHVEFHQUFUVA0KQ0dBVENUR1RDVEFUQ0NBR1RUR0NHVENBQ0NBQUFUR0FBVEdDQUFDQ0FBQVRHVEdDQ1RUVENBQUNUQ1RDDQpBVEdBQUdUR1RHQVRDQVRUR1RHR1RHQUFBQ1RUQ0FUR0dDQUdBQ0dHR0NHQVRUVFRHVFRBQUFHQ0NBQ1Q="


def _make_upload_zone(upload_id, file_types, lang="en"):
    """Helper to create a single dcc.Upload drop zone."""
    return dcc.Upload(
        id=upload_id,
        className="upload-drop-area",
        className_active="upload-drop-area--active",
        children=html.Div(
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
        ),
    )


# ---------------------------------------------------------------------------
# Data-type card definitions
# ---------------------------------------------------------------------------
def get_data_types(lang="en"):
    return [
        {
            "key": "genetic",
            "label": t("upload.data-type.genetic.label", lang),
            "description": t("upload.data-type.genetic.description", lang),
            "formats": ".fasta",
            "upload_id": "upload-genetic-data",
            "upload_label": t("upload.data-type.genetic.upload-label", lang),
        },
        {
            "key": "aligned",
            "label": t("upload.data-type.aligned.label", lang),
            "description": t("upload.data-type.aligned.description", lang),
            "formats": ".fasta, .json",
            "upload_id": "upload-aligned-genetic-data",
            "upload_label": t("upload.data-type.aligned.upload-label", lang),
        },
        {
            "key": "tree",
            "label": t("upload.data-type.tree.label", lang),
            "description": t("upload.data-type.tree.description", lang),
            "formats": ".json",
            "upload_id": "upload-genetic-tree",
            "upload_label": t("upload.data-type.tree.upload-label", lang),
        },
    ]


DATA_TYPES = [
    {
        "key": "genetic",
        "label": "Genetic Data",
        "description": "Sequence or variant data",
        "formats": ".fasta",
        "upload_id": "upload-genetic-data",
        "upload_label": "Upload genetic data (.fasta)",
    },
    {
        "key": "aligned",
        "label": "Aligned Genetic Data",
        "description": "Pre-aligned sequences",
        "formats": ".fasta, .json",
        "upload_id": "upload-aligned-genetic-data",
        "upload_label": "Upload aligned genetic data (.fasta, .json)",
    },
    {
        "key": "tree",
        "label": "Genetic Tree",
        "description": "Phylogenetic tree data",
        "formats": ".json",
        "upload_id": "upload-genetic-tree",
        "upload_label": "Upload genetic tree (.json)",
    },
]

DEFAULT_DATA_TYPE = "genetic"


def _build_data_type_card(dt):
    """Build a single selectable card for a data type."""
    is_default = dt["key"] == DEFAULT_DATA_TYPE
    class_name = "data-type-card selected" if is_default else "data-type-card"

    return html.Button(
        type="button",
        className=class_name,
        id=f"card-{dt['key']}",
        children=[
            html.Div(dt["label"], className="card-label"),
            html.Div(dt["description"], className="card-description"),
            html.Div(dt["formats"], className="card-formats"),
        ],
    )


def get_layout(lang="en"):
    data_types = get_data_types(lang)

    return html.Div(
        [
            html.Div(id="output-file-drop-position-next"),
            html.Div(id="upload-data-output"),
            dcc.Store(id="selected-data-type", data=DEFAULT_DATA_TYPE),
            html.Div(
                id="all-upload-container",
                children=[
                    # ── Header ──
                    html.H2(t("upload.upload-files", lang), className="upload-page-title"),

                    # ── Climatic Data section (REQUIRED) ──
                    html.Div(
                        id="section-climatic",
                        className="upload-section-card",
                        children=[
                            html.Div(
                                className="section-header",
                                children=[
                                    html.Span(t("upload.section-climatic-title", lang), className="section-title"),
                                    create_badge(
                                        text=t("upload.required-badge", lang),
                                        background_color="var(--action-soft-bg)",
                                        text_color="var(--action)",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="climatic-drop-zone",
                                children=[
                                    dcc.Upload(
                                        id="upload-climatic-data",
                                        className="upload-drop-area",
                                        children=html.Div(
                                            [
                                                html.Img(
                                                    src="../../assets/icons/folder-drop.svg",
                                                    className="drop-icon",
                                                ),
                                                html.Div(t("upload.drag-drop", lang), className="drop-main-text"),
                                                html.Div(t("upload.click-browse", lang), className="drop-sub-text"),
                                                create_badge(
                                                    text=".csv",
                                                    background_color="var(--action-soft-bg)",
                                                    text_color="var(--action)",
                                                ),
                                            ],
                                            className="drop-content-inner",
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # ── Additional Data section (CHOOSE ONE) ──
                    html.Div(
                        id="section-additional",
                        className="upload-section-card",
                        children=[
                            html.Div(
                                className="section-header",
                                children=[
                                    html.Span(t("upload.section-additional-title", lang), className="section-title"),
                                    create_badge(
                                        text=t("upload.choose-one-badge", lang),
                                        background_color="var(--action-soft-bg)",
                                        text_color="var(--action)",
                                    ),
                                ],
                            ),
                            html.P(
                                t("upload.section-additional-description", lang),
                                className="section-description",
                            ),
                            # Three selectable cards
                            html.Div(
                                className="data-type-cards",
                                children=[_build_data_type_card(dt) for dt in data_types],
                            ),
                            # Conditional upload zones (all rendered, toggled via callback)
                            html.Div(
                                id="secondary-upload-wrapper",
                                className="secondary-upload-wrapper",
                                children=[
                                    html.Div(
                                        id=f"upload-zone-{dt['key']}",
                                        className="secondary-upload-zone",
                                        style={
                                            "display": "block"
                                            if dt["key"] == DEFAULT_DATA_TYPE
                                            else "none"
                                        },
                                        children=[
                                            html.Div(
                                                className="climatic-drop-zone",
                                                children=[
                                                    _make_upload_zone(
                                                        dt["upload_id"],
                                                        dt["formats"],
                                                        lang,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    )
                                    for dt in data_types
                                ],
                            ),
                        ],
                    ),

                    # ── Continue button with tooltip ──
                    html.Div(
                        className="continue-wrapper",
                        children=[
                            html.Button(
                                [html.Span(t("upload.continue", lang)), html.Span(" →")],
                                id="next-button",
                                className="continue-btn disabled",
                                n_clicks=0,
                                disabled=True,
                            ),
                            html.Span(
                                t("upload.continue-tooltip", lang),
                                id="continue-tooltip",
                                className="continue-tooltip",
                            ),
                        ],
                    ),

                    # ── Helper: "Try with demo data" ──
                    html.Div(
                        [
                            html.Span(t("upload.demo-data-prefix", lang)),
                            html.A(
                                t("upload.demo-data-link", lang),
                                id="upload-test-data",
                                className="demo-data-link",
                            ),
                        ],
                        className="demo-data-helper",
                    ),

                    # Show uploaded files (kept for compatibility)
                    html.Div(id="uploaded-files", className="upload-row"),
                ],
            ),
        ],
    )


layout = get_layout()


# ---------------------------------------------------------------------------
# Callback: card selection → show/hide secondary upload zones
# ---------------------------------------------------------------------------
@callback(
    Output("upload-zone-genetic", "style"),
    Output("upload-zone-aligned", "style"),
    Output("upload-zone-tree", "style"),
    Output("card-genetic", "className"),
    Output("card-aligned", "className"),
    Output("card-tree", "className"),
    Output("selected-data-type", "data"),
    Input("card-genetic", "n_clicks"),
    Input("card-aligned", "n_clicks"),
    Input("card-tree", "n_clicks"),
    State("selected-data-type", "data"),
    prevent_initial_call=True,
)
def select_data_type(n_genetic, n_aligned, n_tree, current_selection):
    triggered = ctx.triggered_id

    key_map = {
        "card-genetic": "genetic",
        "card-aligned": "aligned",
        "card-tree": "tree",
    }
    selected = key_map.get(triggered, current_selection)

    styles = []
    classes = []
    for dt in DATA_TYPES:
        if dt["key"] == selected:
            styles.append({"display": "block"})
            classes.append("data-type-card selected")
        else:
            styles.append({"display": "none"})
            classes.append("data-type-card")

    return *styles, *classes, selected


# ---------------------------------------------------------------------------
# Callback: validate uploads → enable/disable Continue + tooltip
# ---------------------------------------------------------------------------
@callback(
    Output("next-button", "disabled"),
    Output("next-button", "className"),
    Output("continue-tooltip", "className"),
    Input("upload-climatic-data", "contents"),
    Input("upload-genetic-data", "contents"),
    Input("upload-aligned-genetic-data", "contents"),
    Input("upload-genetic-tree", "contents"),
    prevent_initial_call=True,
)
def validate_uploads(climatic, genetic, aligned, tree):
    has_climatic = climatic is not None and climatic != ""
    has_additional = any(
        c is not None and c != "" for c in [genetic, aligned, tree]
    )
    ready = has_climatic and has_additional

    btn_disabled = not ready
    btn_class = "continue-btn" if ready else "continue-btn disabled"
    tooltip_class = "continue-tooltip hidden" if ready else "continue-tooltip"

    return btn_disabled, btn_class, tooltip_class


# ---------------------------------------------------------------------------
# Existing clientside callback (preserved)
# ---------------------------------------------------------------------------
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="next_option_function"),
    Output("output-file-drop-position-next", "children"),
    Input("next-button", "n_clicks"),
    Input("upload-test-data", "n_clicks"),
    Input("params-sections", "id"),
    prevent_initial_call=True,
)
