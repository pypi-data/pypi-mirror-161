=========
Analytics
=========

*Measurement is the foundation of performance.*

Coiled Analytics lets you track Dask usage wherever Dask is run. See the
:doc:`installation instructions <analytics-install>` to get started.

.. toctree::
   :maxdepth: 1
   :hidden:

   analytics-install
   analytics-privacy
   analytics-api

Motivation
----------

When running computations we often ask ourselves questions like the following:

-   Did my computation finish?
-   Did any exceptions occur?
-   How much did that cost me?
-   What is taking most of the time?
-   Why is that cluster still running?

Experienced users know that Dask presents answers to these questions visually
through the `Dask dashboard <https://docs.dask.org/en/stable/dashboard.html>`_.
However, the Dask dashboard only tracks the
real-time performance of a single Dask cluster.  Coiled extends Dask by
tracking many Dask clusters across many users and storing those results over
time for later analysis.  Coiled analytics provides a team-wide view of all
clusters over time.

Analytics Overview
------------------

You can view analytics from ``https://cloud.coiled.io/<your-account-name>/analytics``,
or by selecting ``Analytics`` from the left navigation pane after you login.

You'll see three different views of usage statistics for your Coiled account:

- **Overall account statistics**: Shows total resources used since Coiled account creation. Includes cluster time, compute time, number of tasks and workers, and data processed. Cluster and compute time both measure the number of core hours, where cluster time includes idleness and compute time measure utilization. 

- **Cluster compute usage by account members**: A heat-map of compute time for account members over time.

- **Clusters**: Detailed cluster statistics for each cluster created. You can filter clusters by date by selecting a date in the above view.

You can click on a row to see more detailed performance tracking for a specific cluster including computations, exceptions, and cost per operation.

What information does Coiled Track?
-----------------------------------

Coiled tracks aggregate information about cluster activity including the
following (see :doc:`analytics-privacy`).

-   Basic level statistics

    -   Number of active workers and worker threads
    -   Amount of used and total memory
    -   Software versions of common libraries

-   Performance statistics

    -   Task information, including names, numbers, and compute and transfer durations
    -   Profiling, including which functions and lines of code take the most time
    -   Code snippets surrounding the Dask calls
    -   How long has it been since any work was completed

-   Error tracking

    -   Every user-level exception
    -   Every dask-level exception

-   User-level tracking

    -   Which user within an account created the cluster
    -   Costs (estimated when run on non-Coiled architecture)
    -   Idleness
