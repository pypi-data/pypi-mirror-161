Deploy web applications with Streamlit
======================================

`Streamlit <https://streamlit.io/>`_ is an open-source Python library that makes
it easy to create and share custom web apps for machine learning and data
science. Coiled helps scale Python workloads by provisioning cloud-hosted Dask
clusters on demand.

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/KseGO-XV6cY" title="YouTube video player" style="margin: 0 auto 20px auto; display: block;" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Coiled and Streamlit work great together - Streamlit handles the frontend layout
and interactivity of your web application while Coiled handles the backend
infrastructure for demanding computations.
Since Coiled works anywhere that you can run Python, you can use Coiled
while developing Streamlit apps on your laptop or while interacting with a
hosted Streamlit application - all without having to download your data or
change the way you work.

.. figure:: ../images/coiled-streamlit-example.png
   :width: 100%

Before you start
----------------

You'll first need to create consistent local and remote software environments
with ``dask``, ``coiled``, and the necessary dependencies installed.
If you are unfamiliar with creating software environments, you can first
follow the
:doc:`tutorial on setting up a custom software environment <../tutorials/matching_coiled_senvs>`.

First, you will install ``folium``, ``streamlit``, and :ref:`coiled-runtime <coiled-runtime>`, a Dask meta-package.
Save the following file as ``environment.yml``, replacing ``<x.x.x>`` with the versions
you would like to use. You can get most up-to-date version of coiled-runtime from the latest
`tag <https://github.com/coiled/coiled-runtime/tags>`_ in the public coiled-runtime repository.

.. code:: yaml

   channels:
     - conda-forge
   dependencies:
     - folium=<x.x.x>
     - streamlit=<x.x.x>
     - coiled-runtime=<x.x.x>
     - python=3.9

Next, create a local software environment using the ``environment.yml`` file:

.. code:: bash

    $ conda env create -f environment.yml -n streamlit-example
    $ conda activate streamlit-example

Lastly, create a remote software environment using the ``environment.yml`` file:

.. code:: bash

    $ coiled env create -n streamlit-example --conda environment.yml

Coiled + Streamlit
------------------

The example below uses Coiled and Streamlit to read more than 146 million
records from the NYC Taxi dataset and visualize locations of taxi pickups and dropoffs.
In this guide, you'll learn how to use Coiled to:

1. Read in Parquet files from an Amazon S3 bucket.
2. Filter the dataset based on user inputs.
3. Display the results on a `folium map <https://python-visualization.github.io/folium/>`_

You'll start a Streamlit app locally, but the computations to load,
filter, and generate the folium map will happen on your cloud using Coiled.

.. literalinclude:: streamlit-example.py

Click :download:`here <streamlit-example.py>` to download the above example
script.


How Coiled helps
----------------

Coiled comes into play in the following sections, allowing
you to easily scale the resources available to the Streamlit app on the backend.

First, create your Coiled cluster:

.. literalinclude:: streamlit-example.py
    :lines: 30-46

By using ``@st.cache(allow_output_mutation=True)`` when creating
your Coiled cluster, the Streamlit app will reuse the same connection to the
cluster instead of reconnecting every time the app's state changes 
(see the `caching section <https://docs.streamlit.io/en/stable/caching.html>`__ in the
Streamlit documentation). Additionally, by passing a name to our Coiled cluster in
``cluster = coiled.Cluster(name="coiled-streamlit")``, you
can reconnect to an existing cluster as viewers of your app come and go (see :doc:`../cluster_reuse`).

.. note::
    Coiled will shut down your cluster after 20 minutes of
    inactivity by default to save on compute costs when your Streamlit app
    is not in use. However, if you use ``@st.cache`` on the Coiled cluster and
    expect your Streamlit app to run for long time, you should add a
    ``if client.status == "closed"`` check as shown in the code example above, which
    will recreate the cluster if it has shut down. If you don't use ``@st.cache``,
    then this check is not necessary since a new Coiled cluster will be created
    automatically when another user visits your Streamlit app.

Next, Load the dataset using Dask on your Coiled cluster:

.. literalinclude:: streamlit-example.py
    :lines: 48-70

Here, you used ``.persist()`` to store the dataset in memory on the Coiled cluster. This helps to optimize performance of the Streamlit app, avoiding expensive computations from running each time the app is updated. You also used ``@st.cache`` to optimize performance when calling functions that preload or precompute data with Dask or other computations that only need to run once. Note that ``@st.cache`` does not know the best way to tell if two Dask collections are identical. Therefore, to cache functions that return Dask
collections, you should use ``@st.cache(hash_funcs={dd.DataFrame: dask.base.tokenize})`` and replace ``dd.DataFrame`` with the appropriate datatype that the function returns.

And filter the dataset using Dask on your Coiled cluster:

.. literalinclude:: streamlit-example.py
    :lines: 71-86

By using ``st.spinner("Calculating map data...")``, you provided a spinner
to display a helpful message while the data is loading.

Next steps
----------

To learn more about how to use Streamlit with Coiled,
check out `this Coiled blogpost <https://coiled.io/blog/effective-data-storytelling-with-streamlit-dask-and-coiled/>`_.
