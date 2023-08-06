import coiled
import dask
import prefect
from dask.distributed import Client
from prefect import Flow, task


@task
def load_data():
    """Load some data"""
    return dask.datasets.timeseries("2000", "2005", partition_freq="2w").persist()


@task
def summarize(df):
    """Compute a summary table"""
    return df.groupby("name").aggregate({"x": "sum", "y": "max"}).compute()


@task
def log_summary(df):
    """Log summary result"""
    logger = prefect.context.get("logger")
    logger.info(df)


with Flow(name="taxi-tips") as flow:
    with coiled.Cluster(
        "prefect-example", n_workers=5, software="prefect-example"
    ) as cluster:
        # These tasks rely on a Coiled cluster to run,
        # so you can create them inside the context manager
        client = Client(cluster)
        df = load_data()
        summary = summarize(df)
    # This task doesn't rely on the Coiled cluster to run
    # so it can be outside the context manager
    log_summary(summary)

# run the flow
flow.run()

# To use with Prefect Cloud or Prefect Server:
# Register the flow under your project
# flow.register(project_name="<project-name>")
