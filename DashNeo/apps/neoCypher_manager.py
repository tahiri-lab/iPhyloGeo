from neo4j import GraphDatabase
import pandas as pd
from dotenv import load_dotenv
import os
import secrets
import string
import yaml
from datetime import datetime
# For Neo4j Connection
load_dotenv("my.env")
password = os.getenv("NEO_PASS")


def get_databaseProperties_list():
    q_lineage = "MATCH (n:Lineage) RETURN DISTINCT n.lineage"
    q_protein = "MATCH (n:Protein) RETURN DISTINCT n.protein"
    q_location = "MATCH (n:Location) RETURN DISTINCT n.location"
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with driver.session() as session:
        results_location = session.run(q_location)
        location_list = [record['n.location'] for record in results_location]
        results_protein = session.run(q_protein)
        protein_list = [record['n.protein'] for record in results_protein]
        results_lineage = session.run(q_lineage)
        record_lineage_lt = [record['n.lineage'].split(
            '.')[0] for record in results_lineage]
        lineage_list = list(set(record_lineage_lt))

    location_lt = [item for item in location_list if item is not None]
    protein_lt = [item for item in protein_list if item is not None]
    lineage_lt = [item for item in lineage_list if item is not None]
    return sorted(location_lt), sorted(protein_lt), sorted(lineage_lt)
# -----------Neo4j query function------------------------------


def queryToDataframe(query, col_name_lt):
    # Execute the Cypher query
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with driver.session() as session:
        # session = driver.session()
        results = session.run(query)
    # Transform the results to a DataFrame
        df = pd.DataFrame(results, columns=col_name_lt)
    return df


def getNucleoIdFromSamplesFilter(df):
    accession_lt = []
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    rows_as_dicts = df.to_dict(orient='records')
    for row in rows_as_dicts:
        lineage = row['lineage']
        theDate = row['earliest_date']
        location = row['most_common_country']
        query = """
            MATCH (n:Nucleotide)-[:COLLECTED_IN]->(l:Location)<-[:IN_MOST_COMMON_COUNTRY]-(m:Lineage)
            WHERE l.location = $location AND m.lineage = $lineage AND n.collection_date >= datetime($theDate)
            RETURN n.accession
            ORDER BY n.collection_date
            LIMIT 1
        """
        params = {"location": location, "lineage": lineage, "theDate": theDate}
        with driver.session() as session:
            # session = driver.session()
            results = session.run(query, params)
            record = results.single()
            # print(record)
            if record:
                accession = record["n.accession"]
                accession_lt.append(accession)
             # delete duplication if  we have
        accession_lt = list(set(accession_lt))
    return accession_lt


def getProteinIdFromSamplesFilter(df, protein_name):
    accession_lt = []
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    rows_as_dicts = df.to_dict(orient='records')
    for row in rows_as_dicts:
        lineage = row['lineage']
        theDate = row['earliest_date']
        location = row['most_common_country']
        query = """
            MATCH (n:Protein)-[:COLLECTED_IN]->(l:Location)<-[:IN_MOST_COMMON_COUNTRY]-(m:Lineage)
            WHERE l.location = $location AND m.lineage = $lineage AND n.protein = $protein_name AND n.collection_date >= datetime($theDate)
            RETURN n.accession
            ORDER BY n.collection_date
            LIMIT 1
        """
        params = {"location": location, "lineage": lineage,
                  "protein_name": protein_name, "theDate": theDate}
        with driver.session() as session:
            # session = driver.session()
            results = session.run(query, params)
            record = results.single()
            # print(record)
            if record:
                accession = record["n.accession"]
                accession_lt.append(accession)
        # delete duplication if  we have
        accession_lt = list(set(accession_lt))
    return accession_lt

# ---------Create Input Node and relations based on users sample filter------------------------------------------
# Function to generate a unique random name


def generate_short_id(length=8):
    characters = string.ascii_letters + string.digits
    short_id = ''.join(secrets.choice(characters) for _ in range(length))
    return short_id


def generate_unique_name(nodesLabel):
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with driver.session() as session:
        random_name = generate_short_id()

        result = session.run(
            "MATCH (u:" + nodesLabel + " {name: $name}) RETURN COUNT(u)", name=random_name)
        count = result.single()[0]

        while count > 0:
            random_name = generate_short_id()
            result = session.run(
                "MATCH (u:" + nodesLabel + " {name: $name}) RETURN COUNT(u)", name=random_name)
            count = result.single()[0]

        return random_name


def addInputNeo(nodesLabel, inputNode_name, id_list):
    # Execute the Cypher query
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))

    # Create a new node for the user
    with driver.session() as session:
        session.run(
            "CREATE (userInput:Input {name: $name})", name=inputNode_name)

    # Perform MATCH query to retrieve nodes
    with driver.session() as session:
        result = session.run(
            "MATCH (n:" + nodesLabel + ") WHERE n.accession IN $id_lt RETURN n",
            nodesLabel=nodesLabel,
            id_lt=id_list)

        # Create relationship with properties for each matched node
        with driver.session() as session:
            for record in result:
                other_node = record["n"]
                session.run("MATCH (u:Input {name: $name}), (n:" + nodesLabel + " {accession: $id}) "
                            "CREATE (n)-[r:IN_INPUT]->(u)",
                            name=inputNode_name, nodesLabel=nodesLabel, id=other_node["accession"])
    print("An Input Node has been Added in Neo4j Database!")

# --------====-----------------
# Create Analysis Node and its relationship


def set_properties(data, properties_dict, prefix=""):
    for key, value in data.items():
        if isinstance(value, dict):
            set_properties(value, properties_dict, prefix + key + "&&")
        else:
            properties_dict[key] = value

# Define a function to create a node and set properties


def create_Analysisnode(tx, data):
    query = "CREATE (n:Analysis) SET n = $data"
    tx.run(query, data=data)


def addAnalysisNeo():
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))

    properties_dict = {}
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Set the properties of the node using the yaml_data
    set_properties(config, properties_dict)
    input_name = properties_dict['input_name']
    analysis_name = properties_dict['analysis_name']
    create_time = datetime.now().isoformat()
    # Create node

    with driver.session() as session:
        session.execute_write(create_Analysisnode, properties_dict)
    # Create relationship
    with driver.session() as session:
        session.run("MATCH (u:Input {name: $input_name}), (n:Analysis {analysis_name: $analysis_name}) "
                    "CREATE (u)-[r:FOR_ANALYSIS {create_time: $create_time}]->(n)",
                    input_name=input_name, analysis_name=analysis_name, create_time=create_time)
    print("An Analysis Node has been Added in Neo4j Database!")

# --------------


def create_Outputnode(tx, data):
    query = "CREATE (n:Output) SET n = $data"
    tx.run(query, data=data)


def addOutputNeo():
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    analysis_name = config['analysis']['analysis_name']
    output_name = config['analysis']['output_name']
    if os.path.exists("results/output.csv"):
        df = pd.read_csv('results/output.csv')
        dict_output = df.to_dict('list')
        dict_output['name'] = output_name
        # print(dict_output)
        # Create node

        with driver.session() as session:
            session.execute_write(create_Outputnode, dict_output)
        # Create relationship
        with driver.session() as session:
            session.run("MATCH (o:Output {name: $output_name}), (n:Analysis {analysis_name: $analysis_name}) "
                        "CREATE (n)-[r:WITH_OUTPUT]->(o)",
                        output_name=output_name, analysis_name=analysis_name)
        print("An Output Node has been Added in Neo4j Database!")

    else:
        print("Output file does not exist")

# --------------------------------------


def get_outputdf(output_id):
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    query = """
        MATCH (n:Output {name: $output_id}) 
        RETURN n.window_pos as window_position, n.ref_feature as feature, n.bootstrap_average as bootstrap_average, n.normalized_RF as normalized_RF;
    """
    params = {"output_id": output_id}
    with driver.session() as session:
        results = session.run(query, params)
        record = results.data()[0]
    data_output = {
        'window_position': record['window_position'],
        'feature': record['feature'],
        'bootstrap_average': record['bootstrap_average'],
        'normalized_RF': record['normalized_RF']
    }

    df_output = pd.DataFrame(data_output)

    return df_output


# ----------------------------------------------------


def get_seq_length(nodesLabel, seq_list):
    # Execute the Cypher query
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with driver.session() as session:
        result = session.run(
            "MATCH (n:" + nodesLabel +
            ") WHERE n.accession IN $seq_list RETURN min(n.length)",
            seq_list=seq_list
        )
        length = result.single()[0]
    return length


def get_seqByInputName(input_name):
    # Execute the Cypher query
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with driver.session() as session:
        results = session.run(
            "MATCH (n) -[r:IN_INPUT]->(i:Input {name:$input_name}) RETURN n.accession as accession, n.length as length",
            input_name=input_name
        )
    # Transform the results to a DataFrame
        df = pd.DataFrame(results, columns=['accession', 'length'])
        seq_list = df['accession'].tolist()
        length_min = min(df['length'].tolist())
    return seq_list, length_min


# ---------------------------
# have accession list get location, collection_date, put all the results in a dataframe


def get_dfDayLocation(nodesLabel, seq_list):
    col_name_lt = ['id', 'location', 'collection_date']
    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with driver.session() as session:
        results = session.run(
            "MATCH (n:" + nodesLabel +
            ") WHERE n.accession IN $seq_list RETURN n.accession as id, n.country as location, n.collection_date as collection_date",
            seq_list=seq_list
        )
        # Transform the results to a DataFrame
        df = pd.DataFrame(results, columns=col_name_lt)
    return df


def get_geoRef(location, date_begin, date_end):
    envFactor_list = ['precipitation', 'relative_humidity', 'specific_humidity', 'sky_shortwave_irradiance',
                      'wind_speed_10meters_range', 'wind_speed_50meters_range']
    query = """
        MATCH (n:LocationDAY) 
WHERE n.location = $location
    AND n.date>=datetime($date_begin) AND n.date<=datetime($date_end)
RETURN  n.precipitation as precipitation, n.relative_humidity as relative_humidity, n.specific_humidity as specific_humidity, n.sky_shortwave_irradiance as sky_shortwave_irradiance, n.wind_speed_10meter_srange as wind_speed_10meters_range, n.wind_speed_50meter_srange as wind_speed_50meters_range
    """

    params = {"location": location, "date_begin": date_begin,
              "date_end": date_end}

    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with driver.session() as session:
        results = session.run(query, params)
        df = pd.DataFrame(results, columns=envFactor_list)
    return df


def get_geoOneDay(location, date):
    envFactor_list = ['precipitation', 'relative_humidity', 'specific_humidity', 'sky_shortwave_irradiance',
                      'wind_speed_10meters_range', 'wind_speed_50meters_range']
    query = """
        MATCH (n:LocationDAY) 
WHERE n.location = $location
    AND n.date=datetime($date) 
RETURN  n.precipitation as precipitation, n.relative_humidity as relative_humidity, n.specific_humidity as specific_humidity, n.sky_shortwave_irradiance as sky_shortwave_irradiance, n.wind_speed_10meter_srange as wind_speed_10meters_range, n.wind_speed_50meter_srange as wind_speed_50meters_range
    """

    params = {"location": location, "date": date}

    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with driver.session() as session:
        results = session.run(query, params)
        df = pd.DataFrame(results, columns=envFactor_list)
    return df
# -------------------------------------------


def get_geoMean(locations, dates, interval=3):
    envFactor_list = ['location', 'collection_date', 'precipitation', 'relative_humidity', 'specific_humidity', 'sky_shortwave_irradiance',
                      'wind_speed_10meters_range', 'wind_speed_50meters_range']

    # Generate the location and date_begin and date_end parameters for the query
    # date_begin_lt = [(theDay - pd.DateOffset(days=interval)).strftime(
    #     '%Y-%m-%d') for theDay in dates]
    # date_end_lt = [theDay.strftime('%Y-%m-%d') for theDay in dates]
    # params = [{"location": location, "date_begin": date_begin, "date_end": date_end}
    #           for location, date_begin, date_end in zip(locations, date_begin_lt, date_end_lt)]

    date_begin_lt = [(theDay - pd.DateOffset(days=interval)
                      ).strftime('%Y-%m-%d') for theDay in dates]
    print(locations)
    print(date_begin_lt)
    date_end_lt = [theDay.strftime('%Y-%m-%d') for theDay in dates]
    print(date_end_lt)
    params = [{"location": location, "date_begin": date_begin, "date_end": date_end}
              for location, date_begin, date_end in zip(locations, date_begin_lt, date_end_lt)]

    query = """
    UNWIND $params as param
        MATCH (n:LocationDAY) 
WHERE n.location = param.location
    AND n.date>=datetime(param.date_begin) AND n.date<=datetime(param.date_end)
RETURN n.location as location, param.date_end as collection_date, mean(n.precipitation) as precipitation, mean(n.relative_humidity) as relative_humidity, mean(n.specific_humidity) as specific_humidity, mean(n.sky_shortwave_irradiance) as sky_shortwave_irradiance, mean(n.wind_speed_10meter_srange) as wind_speed_10meters_range, mean(n.wind_speed_50meter_srange) as wind_speed_50meters_range
    """

    driver = GraphDatabase.driver("neo4j+ssc://2bb60b41.databases.neo4j.io:7687",
                                  auth=("neo4j", password))
    with driver.session() as session:
        results = session.run(query, params)
        df = pd.DataFrame(results, columns=envFactor_list)
    return df
