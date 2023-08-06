============
Data Privacy
============

Coiled analytics collects metadata from Dask clusters to help you to understand your work.

It is important to understand this metadata,
including how it is collected,
how it gets to Coiled,
and how it is stored
in order to decide your comfort level and if this solution is right for you.

This document helps you understand how Coiled analytics works.

.. note::

   This is about data privacy in the observability part of the Coiled platform,
   and not the deployment product. For information about Coiled's deployment product,  
   please see :doc:`index`.
   For more information about Coiled analytics itself, please see :doc:`analytics`.


How Coiled Analytics Works
--------------------------

Client Side
~~~~~~~~~~~

Coiled analytics works on any Dask cluster, even those not managed by Coiled.
You activate Coiled analytics by installing a public Python package, importing
Coiled, and calling ``coiled.analytics.register()``:

.. code-block::

   pip install coiled

.. code-block:: python

   import coiled.analytics

   coiled.analytics.register()

This installs a `Dask SchedulerPlugin <https://distributed.dask.org/en/latest/plugins.html>`_
on the local Dask Client, and then uses the Dask-Scheduler connection to send
that plugin to the Scheduler.

The plugin collects Coiled credentials while on the Client, and in particular
captures both ``coiled.token`` for access and the ``coiled.analytics`` namespace
for settings, and sends those up to the Dask Scheduler.

We gather credentials and configuration options on the client-side because that
is more often where users are accustomed to specifying information.  It makes
it easier to configure Coiled without intimate access to the remote environment.

Message Transmission
~~~~~~~~~~~~~~~~~~~~

The SchedulerPlugin sends messages to https://cloud.coiled.io when it first
starts, when your scheduler shuts down, and periodically while running, every
ten seconds or so (this is configurable, search for ``interval`` in the
coiled.analytics configuration).

The plugin sends messages to Coiled using normal HTTPS to regular web endpoints,
authenticated using the API token taken from the client configuration.

These messages are typically small, but if profile information is enabled and
if the cluster is very active then they can grow to be about a megabyte in
size.

Data Collected
--------------

Basic Metrics
~~~~~~~~~~~~~

Coiled tracks basic metrics about your system like the following:

-   The start and stop time of the scheduler
-   The number of currently active workers
-   The amount of memory available within the cluster
-   The aggregated amount of worker-time spent over the lifetime of the cluster
-   Versions of a few key libraries, like Python itself, ``msgpack``, ``cloudpickle``,
    ``lz4`` and everything generally in the ``dask.distributed.versions`` package.
-   The architecture of the system, like x86 or ARM
-   The path of ``python`` used within the system
-   The operating system used, like Linux, OSX, or Windows (remember,
    Coiled.analytics can be used anywhere Dask is run, including personal
    laptops)

Computations
~~~~~~~~~~~~

Coiled optionally tracks information about your code.  This helps to understand
usage, and connect that usage to failures or success.

-   Dask TaskGroups, which contain the following for each group of operations

    -   The name of the operation, like ``read_csv``
    -   How many tasks in the operation, and their states, like waiting, running, in-memory, erred, or released
    -   How much time was spent computing, communicating, and reading from disk
    -   Dependencies with other task groups

-   Exceptions, which include the text of the exception and tracebacks

-   Code snippets around the call to ``dask.compute``.
    This typically includes the context of the function or Jupyter cell that
    called Dask.

If you wish, you can configure Coiled to not send code you can set the following
configuration:

.. code-block:: yaml

   coiled:
     analytics:
       computation:
         code:
           transmit: false

Profiling
~~~~~~~~~

Dask runs a statistical profiler on all user code run within it.  This helps to
identify hot-spots within your code.  Coiled aggregates this information
across users and across time.  This information looks like standard profiling
information, and includes data like the following:

-   filenames
-   line numbers
-   single lines of code contained within the traceback
-   timing information about how many times each line of code was active during
    profiling

If you wish, you can configure Coiled to not send profiling with the following
configuration:

.. code-block:: yaml

  coiled:
    analytics:
      profile:
        transmit: false

Dask Failures
~~~~~~~~~~~~~

When Dask itself fails, such as when a worker fails for some unexpected reason,
or when the state machine enters an undefined state (this should be very rare),
Dask sends a packet of information with status of the state machine.  This
packet of information can be very valuable when diagnosing Dask failures.
Coiled can forward these packets of information to Coiled and associate them to
a particular cluster.

This information tends not to contain user metadata.

If you wish, you can configure Coiled to not send information about Dask
failures with the following configuration:

.. code-block:: yaml

   coiled:
     analytics:
       events:
         allow: []


Events
~~~~~~

The Dask failures are actually sent with a broader eventing system built into
Dask.  You can capture arbitrary user events using the following code:

.. code-block:: python

   from dask.distributed import get_worker


   def some_task():
       score = ...

       get_worker().log_event("scores", {"data": score})


   client.submit(some_task, ...)

Dask will capture the event on the worker, forward it to the Scheduler, which
the plugin will then forward on to Coiled if you include this event type in the
allow-list.

.. code-block:: yaml

   coiled:
     analytics:
       events:
         allow:
         - scores
         - invalid-task-states          # these are the dask failure event names
         - invalid-worker-transition
         - worker-fail-hard

Idle Timeouts
~~~~~~~~~~~~~

Coiled tracks how long your cluster has been idle.
This can be useful either observationally to determine inefficient use of resources
or, if configured, Coiled can actively police your Dask clusters and shut them
down after a suitable limit has been reached.

If you wish, you can configure Coiled to shut down idle clsuters
with the following configuration:

.. code-block:: yaml

   coiled:
     analytics:
       idle:
         timeout: 20 minutes

Note that when running on your own hardware (not managed by Coiled) Coiled can
only make a best effort here through Dask.  We can not guarantee that things
will shut down cleanly (although they usually do) nor do we have any access
over instances or network resources beyond the Dask processes.

Encryption
----------

All metadata is encrypted in flight.  User code is encrypted at rest.

Metadata vs Data
----------------

Coiled tries very hard not to see or store input data at any time.
We view user data as a liability both to our users, and to ourselves.

Coiled does capture metadata however.  We endeavor to help users understand as
much about their computations as they can while touching sensitive data as
little as possible.

User Space Permissions and Risk
-------------------------------

Coiled analytics is designed around user-space permissions.
If users are empowered to use Dask and to make outgoing web connections then
they are able to use ``coiled.analytics`` to track their Dask usage with Coiled.

-   This enables team leads and mangers to have a single view over all Dask work within an organization.

-   If you are a user then this means that Coiled is easy for you to use without
    engaging with your IT department.

-   If you are an IT department then this might be concerning.

    However, you should be equally concerned about letting users use Python on
    machines that can access the web.

All users operate in an environment with some risk and with some implied trust.
We endeavor to not expand that envelope of risk.
Indeed, we try to provide a robust and mature mechanism for Dask users to track
and share performance information in a manner that is secure and traceable.

It beats throwing around notebooks and performance reports in e-mail.
