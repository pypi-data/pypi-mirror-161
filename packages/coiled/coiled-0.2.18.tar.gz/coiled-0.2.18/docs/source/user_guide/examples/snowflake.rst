Faster data transfer with Snowflake
===================================

.. note::

   The ``dask-snowflake`` connector is currently in beta.

`Snowflake <https://www.snowflake.com/>`_ is is a cloud-based data
warehouse, SQL query engine, and analytics service. Coiled helps scale Python
workloads by provisioning cloud-hosted Dask clusters on demand.

Coiled and Snowflake work great together - Snowflake handles the data storage
and SQL query processing while Coiled handles the infrastructure for
creating Dask clusters in your cloud.

.. raw:: html

   <p align="center"><iframe width="560" height="315"
   src="https://www.youtube.com/embed/pinFo1YBD-0" title="YouTube video player"
   frameborder="0" allow="accelerometer; autoplay; clipboard-write;
   encrypted-media; gyroscope; picture-in-picture" allowfullscreen
   style="text-align:center;"></iframe></p>

Loading data from Snowflake into Python typically involves either using
the
`Python Snowflake connector <https://docs.snowflake.com/en/user-guide/python-connector-example.html>`_
to send SQL queries to Snowflake or exporting data from
Snowflake into Parquet format. This works well for small datasets, but can be a
limiting factor when working with larger datasets and more complex queries.
The `Dask-Snowflake connector <https://github.com/coiled/dask-snowflake>`_
helps enables parallel I/O between Snowflake and Dask.

In this guide, you'll learn how to use the ``dask-snowflake`` connector to
read and write large datasets in parallel and perform distributed computations
using Dask clusters on the cloud with Coiled. Click :download:`here <snowflake-example.py>` to download this example.

Before you start
^^^^^^^^^^^^^^^^

You'll first need to create consistent local and remote software environments
with ``dask``, ``coiled``, and the necessary dependencies installed.
If you are unfamiliar with creating software environments, you can first
follow the
:doc:`tutorial on setting up a custom software environment <../tutorials/matching_coiled_senvs>`.

First, you will install ``snowflake-connector-python``, ``dask-snowflake``, and :ref:`coiled-runtime <coiled-runtime>`, a Dask meta-package.
Save the following file as ``environment.yml``, replacing ``<x.x.x>`` with the versions
you would like to use. You can get most up-to-date version of coiled-runtime from the latest
`tag <https://github.com/coiled/coiled-runtime/tags>`_ in the public coiled-runtime repository.

.. code:: yaml

   channels:
     - conda-forge
   dependencies:
     - dask-snowflake=<x.x.x>
     - snowflake-connector-python=<x.x.x>
     - coiled-runtime=<x.x.x>
     - python=3.9

Next, create a local software environment using the ``environment.yml`` file:

.. code:: bash

    $ conda env create -f environment.yml -n snowflake-example
    $ conda activate snowflake-example

Lastly, create a remote software environment using the ``environment.yml`` file:

.. code:: bash

    $ coiled env create -n snowflake-example --conda environment.yml

1. Verify connectivity
^^^^^^^^^^^^^^^^^^^^^^

Define your Snowflake connection parameters as environment variables by running
the following Python code and replacing the user, password, and account with
your own values (see the Snowflake documentation on `account identifiers <https://docs.snowflake.com/en/user-guide/admin-account-identifier.html#account-identifiers>`_):

.. literalinclude:: snowflake-example.py
    :lines: 1-9

.. note::
    Don't have a Snowflake account? You can `sign up here <https://signup.snowflake.com/>`_ for a free trial. 

Verify your Snowflake connection with a query to a sample dataset:

.. literalinclude:: snowflake-example.py
    :lines: 10-30

If the connection and query were successful, then you should see output similar
to the following:

.. code-block::

   (1, 'AAAAAAAABAAAAAAA', datetime.date(1998, 1, 1), None, None, 2450952, 'NY
   Metro', 'large', 597159671, 481436415, '8AM-4PM', 'Bob Belcher', 6, 'More
   than other authori', 'Shared others could not count fully dollars. New
   members ca', 'Julius Tran', 3, 'pri', 6, 'cally', '730', 'Ash Hill',
   'Boulevard', 'Suite 0', 'Georgetown', 'Harmon County', 'OK', '77057', 'United
   States', Decimal('-6.00'), Decimal('0.11'))

.. note::

   We defined the Snowflake username, password, account,
   and warehouse as environment variables and then passed them to the Snowflake
   connector. If you use a different authentication method, you can modify the
   example accordingly. See the Snowflake documentation on
   `using the Snowflake connector for Python <https://docs.snowflake.com/en/user-guide/python-connector-example.html>`_.


2. Launch your cluster
^^^^^^^^^^^^^^^^^^^^^^

Create a Dask cluster on your cloud with Coiled with the environment you created:

.. literalinclude:: snowflake-example.py
    :lines: 31-42

The above example also connects Dask to your Coiled cluster and prints a
link to the Dask dashboard, which you can use later to view the progress of
parallel reads and writes to Snowflake.

3. Generate data
^^^^^^^^^^^^^^^^

You'll first generate a random timeseries of data from ``dask.datasets``:

.. literalinclude:: snowflake-example.py
    :lines: 43-50

You'll use the ``dask-snowflake`` connector to load this sample data into
Snowflake in a later step.


4. Create Snowflake resources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a test warehouse and database to write and read data to and from Snowflake:

.. literalinclude:: snowflake-example.py
    :lines: 51-64


5. Write data in parallel
^^^^^^^^^^^^^^^^^^^^^^^^^

Now you can use ``dask-snowflake`` to write the random timeseries dataset in parallel via a distributed fetch:

.. literalinclude:: snowflake-example.py
    :lines: 65-82

You can monitor the progress of the parallel write operation with the Dask dashboard. After about a minute, the sample data should appear in your Snowflake database. Congrats, you just loaded about 7.7 million records into Snowflake in parallel!

6. Read data in parallel
^^^^^^^^^^^^^^^^^^^^^^^^

Now that you have a timeseries dataset stored in Snowflake, you can read the
data back into your Coiled cluster in parallel via a distributed fetch:

.. literalinclude:: snowflake-example.py
    :lines: 83-95

After a few seconds, you should see the results. As usual, Dask only loads the
data that it needs, since operations in Dask are lazy until computed. You can now
work with Dask as usual to perform computations in parallel.

7. Work with Dask
^^^^^^^^^^^^^^^^^

After you've loaded data on to your Coiled cluster, you can perform typical Dask
operations:

.. literalinclude:: snowflake-example.py
    :lines: 96-99

.. code-block:: python

   result = ddf.X.mean().compute()
   print(result)

After the computation completes, you should see output similar to the following:

.. code-block:: text

   0.00020641088610962797


Lastly, you can stop the running cluster using the following commands.
By default, clusters will shutdown after 20 minutes of inactivity (see :doc:`../cluster_management`).

.. literalinclude:: snowflake-example.py
    :lines: 100-104

Next Steps
^^^^^^^^^^
You can run through the example again and increase the size of the sample
dataset or increase the size of your Coiled cluster with the ``n_workers`` argument.
You can also step through this guide using any other datasets you have stored in Snowflake.
Check out Coiled's `blogpost <https://coiled.io/blog/snowflake-and-dask/>`_ for more details
on how to use Snowflake and Dask.
