# aws-athena-weather-data

## Steps

1. Clone the repo to your local machine
2. Edit `config.yml` with your parameters
3. From the main directory of the repo execute the following command to build the docker image, while replacing the argument values with your AWS keys:
    ```
    docker build \
    -t wave:1.0 \
    --build-arg ACCESS_KEY={your access key} \
    --build-arg SECRET_KEY={your secret key} \
    .
    ```
    The AWS keys will be set as environment variables in the docker image  

4. Then execute `docker run --publish 5000:5000 wave:1.0` to run the docker image in a container
5. After a few seconds, the results for each question will be printed in the terminal

## Repo Contents

- README.md
- Dockerfile
- config.yml **(set configuration parameters here)**
- files
    - Station Inventory EN.csv **(input csv file)**
    - weather_data.xlsx **(output xlsx file)**
- src
    - requirements.txt
    - main.py **(main method)**
    - enums.py
    - contants.py **(the SQL queries used to answer the questions are defined here)**
    - utils.py **(some helper functions)**
    - aws_wrapper.py **(a wrapper class around the AWS SDK)**

## Comments and Assumptions

- There are about ~90 weather stations for Toronto. We're only limiting the scope of this demo to the "Toronto City" station, which has data from 2002 onwards
- For paritioning the data in S3, we're using Hive style format (i.e., the file path includes the names of the partition keys and their values)
- To query the data from S3, the code uses the AWS Python SDK to first create a paritioned external table in Athena, and then query the data into a Pandas DataFrame, for each of the queries defined in constants.py

## SQL Queries
The SQL queries are defined in constants.py
- Query 1 returns the max and min temperature for the given year
- Query 2 returns the % difference between the avg temperature for the given year versus the avg of the 2 years prior to the given year (e.g., if the given year is 2023, we compare its mean to the avg temperature of 2022 and 2021)
- Query 3 calculates the % difference between the avg temperature of each month and the avg annual temperature, as well as the absolute difference between each month and its previous month