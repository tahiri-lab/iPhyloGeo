import pandas as pd
from datetime import datetime, timedelta
import yaml
# from neo4j.time import DateTime

from apps import neoCypher_manager

envFactor_list = ['precipitation', 'relative_humidity', 'specific_humidity', 'sky_shortwave_irradiance',
                  'wind_speed_10meters_range', 'wind_speed_50meters_range']
# (1) have accession list get location, collection_date, put all the results in a dataframe


def get_day_location():
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    seq_lt = config['seqinfo']['accession_lt']
    # print(len(seq_lt))
    data_type = config['params']['data_type']
    if data_type == 'dna':
        df_day_location = neoCypher_manager.get_dfDayLocation(
            'Nucleotide', seq_lt)
    else:
        df_day_location = neoCypher_manager.get_dfDayLocation(
            'Protein', seq_lt)
    # df_day_location.set_index('id', inplace=True)
    df_day_location['collection_date'] = df_day_location['collection_date'].apply(
        lambda x: datetime.strptime(x.strftime('%Y-%m-%d'), '%Y-%m-%d').date()
    )
    # df_day_location['collection_date'] = df_day_location['collection_date'].apply(
    #     lambda x: x.to_native())
    # df_day_location['collection_date'] = pd.to_datetime(
    #     df_day_location['collection_date']).dt.date
    return df_day_location
# --------------------------------------------------------------
# (2)  Function to generate mean climate information


def get_climate_info(row, interval=3):
    location = row['location']
    date_end = row['collection_date'].strftime('%Y-%m-%d')
    date_begin = row['collection_date'] - pd.DateOffset(days=interval)
    date_begin = date_begin.strftime('%Y-%m-%d')

    df = neoCypher_manager.get_geoRef(location, date_begin, date_end)
    geo_dict = {col: round(df[col].mean(), 2) for col in df.columns.tolist()}
    return geo_dict


def get_climate_Onedayinfo(row):
    location = row['location']
    date = row['collection_date'].strftime('%Y-%m-%d')

    df = neoCypher_manager.get_geoOneDay(location, date)
    geo_dict = {col: df[col] for col in df.columns.tolist()}
    return geo_dict
# --------------------------------------------------------
# (3) Concatenate Seq and Geo


def get_seq_oneDayGeo():
    # Get the df_day_location DataFrame
    df_day_location = get_day_location()

    # Apply the function to each row of df_day_location and update the DataFrame with climate information
    df_day_location['climate_info'] = df_day_location.apply(
        lambda row: get_climate_Onedayinfo(row), axis=1)
    # Extract keys from the first row of the climate_info column
    keys = df_day_location['climate_info'].iloc[0].keys()

    # Create new columns for each key and extract the corresponding values
    for key in keys:
        df_day_location[key] = df_day_location['climate_info'].apply(
            lambda x: x.get(key))

    # Drop the original climate_info column
    df_day_location.drop('climate_info', axis=1, inplace=True)
    return df_day_location


def get_seq_MeanGeo(interval=3):
    # Get the df_day_location DataFrame
    df_day_location = get_day_location()

    # Apply the function to each row of df_day_location and update the DataFrame with climate information
    df_day_location['climate_info'] = df_day_location.apply(
        lambda row: get_climate_info(row, interval), axis=1)
    # Extract keys from the first row of the climate_info column
    keys = df_day_location['climate_info'].iloc[0].keys()

    # Create new columns for each key and extract the corresponding values
    for key in keys:
        df_day_location[key] = df_day_location['climate_info'].apply(
            lambda x: x.get(key))

    # Drop the original climate_info column
    df_day_location.drop('climate_info', axis=1, inplace=True)
    return df_day_location


# df = get_seq_MeanGeo(interval=3)
# print(df)


# ----------------------------------------
# trying other possible option
def neo_climate_mean(interval=3):
    # Get the df_day_location DataFrame
    df_day_location = get_day_location()
    locations = df_day_location['location'].tolist()
    dates = df_day_location['collection_date'].tolist()
    df_withGeo = neoCypher_manager.get_geoMean(locations, dates, interval=3)
    return df_withGeo


# df = neo_climate_mean(interval=3)
# print(df)


# -----------------------------------------------------------------
# To make the table in the web appear normal
def df_colnamesTransfer(df, oldcols_lt, newcols_lt):
    if df.columns.tolist() == oldcols_lt:
        df.rename(columns=dict(zip(oldcols_lt, newcols_lt)), inplace=True)

        return df
    else:
        print("column name error")
