from prefect import Flow, task
from prefect.executors import DaskExecutor


@task
def inc(x):
    return x + 1


@task
def double(x):
    return x * 2


@task
def add(x, y):
    return x + y


@task
def sum_all(z):
    return sum(z)


with Flow("inc-double-add-sum") as flow:
    input = range(10)
    a = inc.map(input)
    b = double.map(input)
    c = add.map(x=a, y=b)
    total_sum = sum_all(c)

coiled_executor = DaskExecutor(
    # tell the DaskExecutor to run on Coiled
    cluster_class="coiled.Cluster",
    # Coiled-specific keyword arguments
    cluster_kwargs={
        "n_workers": 5,
        # replace "account-name" with your account name
        "software": "prefect-example",
        # set shutdown_on_close to False to re use the cluster
        "shutdown_on_close": True,
        # name of the cluster, for easy reference
        "name": "prefect-executor",
    },
)

# run the flow
flow.run(executor=coiled_executor)

# To use with Prefect Cloud or Prefect Server:
# Register the flow under your project
# flow.register(project_name="<project-name>")
