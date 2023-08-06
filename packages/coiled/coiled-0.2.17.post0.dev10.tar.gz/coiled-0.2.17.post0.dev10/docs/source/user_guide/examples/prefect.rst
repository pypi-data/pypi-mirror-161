Workflow automation with Prefect
================================

`Prefect <https://www.prefect.io/>`_ is a workflow management system
you can use to automate your data pipelines. Prefect is built on
top of Dask, so you can execute workflows in parallel and
use Coiled to execute those workflows on the cloud.

In this example, we'll cover two main ways to use Coiled with Prefect:

#. Use the ``LocalExecutor`` to run Dask computations on a Coiled cluster
#. Use the ``DaskExecutor`` to execute Prefect tasks in parallel on a Coiled cluster

Before you start
~~~~~~~~~~~~~~~~

You'll first need to create consistent local and remote software environments
with ``dask``, ``coiled``, ``prefect``, and the necessary dependencies installed.
If you are unfamiliar with creating software environments, you can first
follow the
:doc:`tutorial on setting up a custom software environment <../tutorials/matching_coiled_senvs>`.

First, you will install :ref:`coiled-runtime <coiled-runtime>`, a Dask meta-package, and ``prefect``.
Save the following file as ``environment.yml``, replacing ``<x.x.x>`` with the versions
you would like to use. You can get most up-to-date version of coiled-runtime from the latest
`tag <https://github.com/coiled/coiled-runtime/tags>`_ in the public coiled-runtime repository.

.. code:: yaml

   channels:
     - conda-forge
   dependencies:
     - prefect=<x.x.x>
     - coiled-runtime=<x.x.x>
     - python=3.9

Next, create a local software environment using the ``environment.yml`` file:

.. code:: bash

    $ conda env create -f environment.yml -n prefect-example
    $ conda activate prefect-example

Lastly, create a remote software environment using the ``environment.yml`` file:

.. code:: bash

    $ coiled env create -n prefect-example --conda environment.yml

Terminology
~~~~~~~~~~~

In this example, you'll see three key Prefect terms: ``Flows``, ``Tasks``, ``Executors``.
A Prefect `flow <https://docs.prefect.io/core/concepts/flows.html>`_
is a collection of individual steps, or `tasks <https://docs.prefect.io/core/concepts/tasks.html>`_.
A task is similar to a function; it accepts arguments, does something with them, and
optionally returns a result. You can create a Prefect task using the ``@task`` decorator.
`Executors <https://docs.prefect.io/orchestration/flow_config/executors.html>`_
represent the logic for how and where a ``Flow`` should run. The default executor is the
``LocalExecutor``.

.. note::

    For demonstration purposes, these examples use ``flow.run()`` to run the ``Flow``.
    Though this works for simple flows, for running and monitoring many flows, Prefect
    recommends using Prefect Cloud or Prefect Server
    (see the `Prefect documentation on orchestration <https://docs.prefect.io/orchestration/>`_).

.. _prefect-local-executor:

Using the ``LocalExecutor``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, you'll use the default ``LocalExecutor``.
This is often the preferred method of scaling Dask
computations you have tested locally to the cloud.
Prefect will manage running your ``Flow`` locally, however,
individual tasks relying on Dask will be run on the cloud
with Coiled. This can be helpful if
only some of your tasks are memory- or compute- bound.
You can use a Coiled cluster for a subset of your tasks, 
then proceed with running subsequent tasks locally.

.. figure:: ../images/coiled-prefect-task.png
   :width: 100%
   :alt: Conceptual diagram using Coiled to run a Dask cluster selectively for Prefect tasks.

The example below uses Prefect to define three ``Tasks``:

#. ``load_data`` uses Dask to lazily read in a random timeseries of data from ``dask.datasets``.
#. ``summarize`` uses Dask to compute aggregations of multiple columns. 
#. ``log_summary`` uses the Prefect logger to log the result of ``summarize``.

.. literalinclude:: prefect-task.py
    :lines: 1-24

The three tasks are put together to build a pipeline using the ``Flow`` context:

.. literalinclude:: prefect-task.py
    :lines: 27-

The tasks ``load_data`` and ``summarize`` are computationally expensive, and therefore run from within the Coiled cluster context. The last task ``log_summary`` does not require any computation, therefore it is created outside the cluster context.

Now, when you run this flow with ``flow.run()``, ``load_data`` and ``summarize`` will
run your Dask computations the cloud while ``log_summary`` will run locally.
Click :download:`here <prefect-task.py>` to download the complete example.

.. _prefect-dask-executor:

Using the ``DaskExecutor``
~~~~~~~~~~~~~~~~~~~~~~~~~~

With Prefect's `DaskExecutor <https://docs.prefect.io/orchestration/flow_config/executors.html#daskexecutor>`_,
you can run an entire ``Flow`` on a Coiled cluster. This is helpful
if you have "mapped" tasks, where a task is mapped over an iterable input (see the `Prefect documentation on mapping <https://docs.prefect.io/core/concepts/mapping.html>`_).

.. figure:: ../images/coiled-prefect-executor.png
   :width: 100%
   :alt: Conceptual diagram using Coiled to run an entire Prefect flow.

In this example, you'll use Prefect to define the following ``Flow``:

.. literalinclude:: prefect-executor.py
    :lines: 1-30

The ``inc`` and ``double`` tasks are mapped over ``inputs``, in this case, a sequence of integers 0 through 9.
Then, ``add`` is mapped over the results from ``inc`` and ``double``. Lastly ``sum_all`` reduces the sequence
of integers to a single value by summing all elements. There is parallelism in these tasks, since ``inc``, ``double``, and ``add`` can be evaluated independently.

Now that you have defined the ``Flow``, you can use the ``DaskExecutor`` to take advantage of this parallelism:

.. literalinclude:: prefect-executor.py
    :lines: 32-

By setting the ``cluster_class`` argument to use "coiled.Cluster", you are able to use Coiled to run this ``Flow`` on the cloud. For demonstration purposes, ``shutdown_on_close=True``, however, in practice you may want to reuse the same cluster across flows (see :doc:`../cluster_reuse`). Click :download:`here <prefect-executor.py>` to download the complete example.

Key takeaways
~~~~~~~~~~~~~

In the :ref:`first example <prefect-local-executor>`, you used Prefect and Coiled to automate
your data pipeline workflow and run it on the cloud. You used Prefect's ``LocalExecutor`` to manage the
client-side interaction. You used Dask to manage reading in
and calculating some summary statistics for a large Parquet dataset
of ~84 million rows and Coiled to manage deployment to the cloud.

In the :ref:`second example <prefect-dask-executor>`, you configured Prefect's ``DaskExecutor`` to run
the "inc-double-add-sum" ``Flow`` on the cloud using Coiled. By using
the ``DaskExecutor``, you were able to take advantage of the parallelism
in this ``Flow`` using a common "map/reduce" framework.

Next Steps
~~~~~~~~~~

You can check out `this blog post <https://coiled.io/blog/big-data-workflow-automation-with-prefect-and-coiled>`_
to see how to use Prefect's ResourceManager to dynamically select whether to run your tasks locally or in the cloud.

Watch the video tutorial below on using Prefect with Dask and Coiled to see how to take advantage
of Prefect's many features, such as automatically retrying task execution, setting
up automatic event notifications via the Slack integration, and monitoring it all with `Prefect Cloud <https://www.prefect.io/cloud/>`_.

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/awXYHAkY2To" title="YouTube video player" frameborder="0" style="margin: 0 auto 20px auto; display: block;" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
