=======
Install
=======

This document helps you to set up Coiled analytics in your own Dask clusters
running outside of Coiled. If you are launching clusters though Coiled, then these analytics are already set up for you. You can view them from ``https://cloud.coiled.io/<your-account-name>/analytics``.

You will need to install the ``coiled`` client library onto your local
machine::

   pip install coiled

Log In
------

You will need to have a Coiled account in order to use Coiled analytics.
You can go to https://cloud.coiled.io and sign up with Google, Github, or with a
username and password.

After that you can go to https://cloud.coiled.io/profile where you can click *Create
an API token*.  This will leave you with a command line argument you can run to
install the token on your local machine::

   coiled login --token XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

This writes your username, account, and API token into ``~/.config/dask/coiled.yaml``
in the following form:

.. code-block:: yaml

   coiled:
     user: my-username
     account: my-username
     token: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Dask uses this information to authenticate with Coiled.


Local Interactive Usage
-----------------------

If you're running Dask interactively from the machine where you just just
logged in (such as from a Jupyter notebook or script) then you can ask your
Dask client to connect to Coiled with the following lines:

.. code-block:: python

   from dask.distributed import Client

   client = Client()  # Your code from before

   import coiled.analytics

   coiled.analytics.register()  # connect Dask cluster to Coiled

This works as long as your Client is local.  Your cluster can be running on a
remote cluster though.  We will copy your local Coiled API credentials and ship
them to the remote cluster.


Scheduler Preload
-----------------

Alternatively, if you don't want to modify your code to include the
``coiled.analytics.register()`` line then you can run this as a preload on the
``dask-scheduler`` command::

   dask-scheduler --preload coiled.analytics

If you want to apply all this to your code automatically, or if you can not
easily modify the dask-scheduler command (perhaps because it is run for you
with a project like ``dask-kubernetes`` or ``dask-cloudprovider``, then you can
register ``coiled.analytics`` as a preload script.  This can be done in one of
two ways:

1.  Place the following yaml into ``~/.config/dask/`` or ``/etc/dask``:

    .. code-block:: yaml

       distributed:
         scheduler:
           preload:
           - coiled.analytics

2.  Set the following environment variable::

       DASK_DISTRIBUTED__SCHEDULER__PRELOAD=coiled.analytics

If you do this then you need to make sure that your API tokens are available on
the machines where the scheduler is run.


Remote Configuration
--------------------

If you want to use Coiled on jobs that are launched remotely then you will have
to copy the Coiled configuration to wherever the Client or Scheduler are run.
You can do this either by copying the ``~/.config/dask/coiled.yaml`` file
created earlier, or by setting the following environment variables::

   DASK_COILED__USER="my-account"
   DASK_COILED__ACCOUNT="my-account"
   DASK_COILED__TOKEN="XXXXXXXXXXXXXXXXX"

