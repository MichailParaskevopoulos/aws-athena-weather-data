import pandas as pd
from datetime import date
import yaml
import awswrangler as wr
import os

from constants import (
    QUERY_1, 
    QUERY_2, 
    QUERY_3
)
from utils import (
    get_station_id,
    get_weather_data,
    clean_data,
    write_to_excel
)
from aws_wrapper import AwsWrapper


if __name__ == '__main__':
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)

    # input params
    input_file_path = config['input_csv_config']['file_path']
    rows_to_skip = config['input_csv_config']['rows_to_skip']
    year_0 = config['input_csv_config']['year']
    timeframe = config['input_csv_config']['timeframe']
    city = config['input_csv_config']['city']
    station_name = config['input_csv_config']['station_name']

    # output file params
    output_file_name = config['output_config']['file_name']

    # AWS params
    bucket = config['s3_config']['bucket']
    object_name = config['s3_config']['object_name']
    partitions = config['athena_config']['partitions']
    athena_s3_output = config['athena_config']['athena_s3_output']
    table_name = config['athena_config']['table_name']
    dataset_name = config['athena_config']['dataset_name']

    # ENV variables
    ACCESS_KEY = os.getenv(config['aws_credentials']['ACCESS_KEY'])
    SECRET_KEY = os.getenv(config['aws_credentials']['SECRET_KEY'])

    aws = AwsWrapper(
        region = 'us-east-2',
        aws_access_key_id = ACCESS_KEY,
        aws_secret_access_key = SECRET_KEY
    )
    
    # main method
    today = date.today()
    if timeframe == 'hourly':
        timeframe_value = 1
    elif timeframe == 'daily':
        timeframe_value = 2
    elif timeframe == 'monthly':
        timeframe_value = 3
    else:
        timeframe_value = 2

    df_station_inventory = pd.read_csv(input_file_path, skiprows=rows_to_skip)

    station_id = get_station_id(
        station_inventory = df_station_inventory,
        station_name = station_name
    )

    for i in range(0,3):
        year = year_0 - i
        
        if year > today.year:
            continue

        weather_df = get_weather_data(
            year = year,
            station_id = station_id,
            timeframe_value = timeframe_value
        )

        clean_df = clean_data(
            city = city,
            input_df = weather_df,
            dim_df = df_station_inventory
        ) 

        clean_df.to_csv(f"{output_file_name}.csv", index=False)

        aws.upload_to_s3(
            file_name = output_file_name,
            object_name = object_name,
            bucket = bucket,
            city = city,
            year = year
        )

        write_to_excel(
            excel_file_name = f"{output_file_name}.xlsx",
            df = clean_df,
            city = city,
            year = year
        )

    aws.create_athena_table(
        df = clean_df,
        table_name = table_name,
        dataset_name = dataset_name,
        bucket = bucket,
        athena_s3_output = athena_s3_output,
        partitions = partitions
    )

    # Answer to numerical questions
    query_1_result = aws.athena_to_pandas(
        query=QUERY_1.format(year_0=year_0),
        database=dataset_name
    )

    print(query_1_result)

    query_2_result = aws.athena_to_pandas(
        query=QUERY_2.format(year_0=year_0),
        database=dataset_name
    )

    print(query_2_result)

    query_3_result = aws.athena_to_pandas(
        query=QUERY_3.format(year_0=year_0),
        database=dataset_name
    )

    print(query_3_result)