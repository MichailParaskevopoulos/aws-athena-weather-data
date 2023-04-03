# aws-athena-weather-data

## Steps

1. Clone repo to your local machine
2. Edit `config.yml` with your parameters
3. From the main directory of the repo execute the following command to build the docker image, while replacing the argument values with your AWS keys:
    ```
    docker build \
    -t wave:1.0 \
    --build-arg ACCESS_KEY=AKIATPOZRPAYOOSG3XH5 \
    --build-arg SECRET_KEY=BaAQlsqjaCiSdJaF6sFEgE5CPttplcIcaCbDfDkj \
    .
    ```
    The AWS keys will be set as environment variables in the docker images.  
    
4. Then execute `docker run --publish 5000:5000 wave:1.0` to run the docker image in a container
5. After a few seconds, the results for each question will be printed in the terminal

## Repo Contents

- README.md
- Dockerfile
- config.yml (set configuration parameters here)
- files
    - Station Inventory EN.csv (input csv file)
    - weather_data.xlsx (output xlsx file)
- src
    - requirements.txt
    - main.py (main method)
    - enums.py
    - contants.py (the SQL queries used to answer the questions are defined here)
    - utils.py (some helper functions)
    - aws_wrapper.py (a wrapper class around the AWS SDK)

## Comments and Assumptions

- There are about ~90 weather stations for Toronto. We're only limiting the scope of this demo to the "Toronto City" station, which has data from 2002 onwards
- For paritioning the data in S3, we're using Hive style format (i.e., the file path includes the names of the partition keys and their values)
- To query the data from S3, we first create a paritioned external table in Athena, and then use the Python SDK to query the data into a Pandas DataFrame