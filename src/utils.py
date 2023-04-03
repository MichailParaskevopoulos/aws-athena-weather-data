"""
    Helper functions
"""

import pandas as pd
from os.path import exists
from datetime import date
import re  

today = date.today()

def get_station_id(
    station_inventory: pd.DataFrame, 
    station_name: str
) -> str:
    """
    Function to get the station ID for a given station name
    """
    try:
        station_id = station_inventory[station_inventory['Name'] == station_name][['Station ID']].values[0][0]
    except IndexError:
        print(f"'{station_name}' not found in the Station Invetory")
    
    return station_id

def get_weather_data(
    year: int,
    station_id,
    timeframe_value: int
) -> pd.DataFrame:
    """
    Function to get the weather data from Canada Climate Services
    """
    url = f"https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station_id}&Year={year}&timeframe={timeframe_value}&submit=Download+Data"
    output_df = pd.read_csv(url)
    output_df['Station ID'] = station_id

    return output_df

def rename_df_columns(
    df: pd.DataFrame
) -> None:

    renamed_columns = []
    for column in df.columns:
        renamed_column = column.lower().strip()
        renamed_column = re.sub("°|\(|\)", "", renamed_column)
        renamed_column = re.sub("\s|/", "_", renamed_column)

        renamed_columns.append(
            renamed_column
        )

    df.columns = renamed_columns

def clean_data(
    city: str,
    input_df: pd.DataFrame,
    dim_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Function for cleaning the raw data.
    Transformations:
        - drop any future dates
        - merge weather data with input station inventory
        - rename columns to replace illegal characters according to https://docs.aws.amazon.com/athena/latest/ug/tables-databases-columns-names.html
    """
    df = input_df[input_df['Date/Time'] < today.strftime("%Y-%m-%d")]

    output_df = pd.merge(df, dim_df, how='left', on = 'Station ID')

    rename_df_columns(
        df = output_df
    )

    output_df.drop('year', axis=1, inplace=True)

    return output_df

def write_to_excel(
    excel_file_name: str,
    df: pd.DataFrame,
    city: str,
    year: int
) -> None:
    """
    Function for writing output dataframe to excel
    """
    if not exists(excel_file_name):
        mode = "w"
        if_sheet_exists = None
    else:
        mode = "a"
        if_sheet_exists = "replace"

    with pd.ExcelWriter(excel_file_name, mode=mode, if_sheet_exists=if_sheet_exists) as writer:
        df.to_excel(writer, sheet_name=f"{city}_{year}")