# Set environment variables related to Snowflake
import os

os.environ["SNOWFLAKE_USER"] = "<YOUR-USERNAME>"
os.environ["SNOWFLAKE_PASSWORD"] = "<YOUR-PASSWORD>"
os.environ["SNOWFLAKE_ACCOUNT"] = "<YOUR-ACCOUNT>"
# leave this line as-is, you'll use it in a later step
os.environ["SNOWFLAKE_WAREHOUSE"] = "dask_snowflake_wh"

# Verify Snowflake connectivity
import snowflake.connector

ctx = snowflake.connector.connect(
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    account=os.environ["SNOWFLAKE_ACCOUNT"],
)

cs = ctx.cursor()

schema = "TPCDS_SF100TCL"
table = "CALL_CENTER"

cs.execute("USE SNOWFLAKE_SAMPLE_DATA")
cs.execute("SELECT * FROM " + schema + "." + table)

one_row = str(cs.fetchone())

print(one_row)

# Create a Dask cluster with Coiled
import coiled
from dask.distributed import Client

cluster = coiled.Cluster(
    name="snowflake-example",
    software="snowflake-example",
)
# connect Dask to your Coiled cluster
client = Client(cluster)
print("Dashboard:", client.dashboard_link)

# Generate synthetic data
import dask

ddf = dask.datasets.timeseries(
    start="2021-01-01",
    end="2021-03-31",
)

# Create a warehouse and database in Snowflake
ctx = snowflake.connector.connect(
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
)

cs = ctx.cursor()

cs.execute("CREATE WAREHOUSE IF NOT EXISTS dask_snowflake_wh")
cs.execute("CREATE DATABASE IF NOT EXISTS dask_snowflake_db")
cs.execute("USE DATABASE dask_snowflake_db")

# Write data to Snowflake in parallel
from dask_snowflake import to_snowflake

connection_kwargs = {
    "user": os.environ["SNOWFLAKE_USER"],
    "password": os.environ["SNOWFLAKE_PASSWORD"],
    "account": os.environ["SNOWFLAKE_ACCOUNT"],
    "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
    "database": "dask_snowflake_db",
    "schema": "PUBLIC",
}

to_snowflake(
    ddf,
    name="dask_snowflake_table",
    connection_kwargs=connection_kwargs,
)

# Read data from Snowflake in parallel
from dask_snowflake import read_snowflake

ddf = read_snowflake(
    query="""
        SELECT *
        FROM dask_snowflake_table;
    """,
    connection_kwargs=connection_kwargs,
)

print(ddf.head())

# Work with Dask as usual
result = ddf.X.mean().compute()
print(result)

# Close the cluster
cluster.close()

# Close the client
client.close()
