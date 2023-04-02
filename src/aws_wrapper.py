import boto3
import awswrangler as wr
import pandas as pd
from enums import AthenaDataTypes

class AwsWrapper:
    def __init__(
        self, 
        region: str,
        aws_access_key_id: str,
        aws_secret_access_key: str
    ):
        self.region = region
        self.session = boto3.Session(
            region_name="us-east-2",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def upload_to_s3(
        self,
        file_name: str,
        object_name: str,
        bucket: str,
        city: str,
        year: int
    ) -> None:

        s3_client = self.session.client('s3')

        object_name = f"city={city}/year={year}/{object_name}.csv"

        s3_client.upload_file(f"{file_name}.csv", bucket, object_name)

    def __execute_athena_query(
        self,
        query: str,
        athena_s3_output: str
    ) -> int:

        client = self.session.client('athena')

        config = {'OutputLocation': athena_s3_output}

        r = client.start_query_execution(
            QueryString = query,
            ResultConfiguration = config
        )

        return r['ResponseMetadata']['HTTPStatusCode']
    
    def create_athena_table(
        self,
        df: pd.DataFrame,
        table_name: str,
        dataset_name: str,
        bucket: str,
        athena_s3_output: str,
        partitions: dict = {}
    ) -> None:

        columns = []
        for index, dtype in df.dtypes.items():
            data_type = AthenaDataTypes(dtype).name
            column_name = index

            columns.append(
                f'`{column_name}` {data_type}'
            )

        ddl_columns = ','.join(i for i in columns)

        ddl_partitions = ','.join([f'`{k}` {v}' for (k, v) in partitions.items()])

        query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS `{dataset_name}`.`{table_name}` ({ddl_columns})
        PARTITIONED BY ({ddl_partitions})
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION 's3://{bucket}/'
        TBLPROPERTIES (
        'skip.header.line.count' = '1'
        );
        """

        self.__execute_athena_query(
            query = query,
            athena_s3_output = athena_s3_output
        )

        repair_query = f"""
        MSCK REPAIR TABLE `{dataset_name}`.`{table_name}`;
        """

        self.__execute_athena_query(
            query = repair_query,
            athena_s3_output = athena_s3_output
        )

    def athena_to_pandas(
        self,
        query: str,
        database: str
    ) -> pd.DataFrame:

        return wr.athena.read_sql_query(
            sql=query, 
            database=database,
            boto3_session=self.session
        )