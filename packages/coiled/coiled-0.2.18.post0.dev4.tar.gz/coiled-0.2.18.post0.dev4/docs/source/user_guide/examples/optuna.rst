Hyperparameter tuning with Optuna
=================================

`Optuna <https://optuna.org/>`_ is a popular Python library for hyperparameter
optimization. In this guide you'll learn to optimize an `XGBoost <https://xgboost.readthedocs.io/en/latest/>`_ classification model with Optuna and scale your work using Dask and Coiled.

Before you start
----------------

You'll first need to create consistent local and remote software environments
with ``dask``, ``coiled``, and the necessary dependencies installed.
If you are unfamiliar with creating software environments, you can first
follow the
:doc:`tutorial on setting up a custom software environment <../tutorials/matching_coiled_senvs>`.

First, you will install ``optuna``, ``xgboost``, and :ref:`coiled-runtime <coiled-runtime>`, a Dask meta-package.
Save the following file as ``environment.yml``, replacing ``<x.x.x>`` with the versions
you would like to use. You can get most up-to-date version of coiled-runtime from the latest
`tag <https://github.com/coiled/coiled-runtime/tags>`_ in the public coiled-runtime repository.

.. code:: yaml

   channels:
     - conda-forge
   dependencies:
     - xgboost=<x.x.x>
     - optuna=<x.x.x>
     - coiled-runtime=<x.x.x>
     - python=3.9
     - pip
     - pip:
       - dask-optuna=<x.x.x>

Next, create a local software environment using the ``environment.yml`` file:

.. code:: bash

    $ conda env create -f environment.yml -n optuna-example
    $ conda activate optuna-example

Lastly, create a remote software environment using the ``environment.yml`` file:

.. code:: bash

    $ coiled env create -n optuna-example --conda environment.yml

Optuna in a nutshell
--------------------

Optuna has three main concepts:

- Objective function: This is a function that depends on the hyperparameters
  in your model that you would like to optimize. For example, it's common to
  maximize a classification model's prediction accuracy (i.e. the objective
  function would be the accuracy score).

- Trial: a single evaluation of the objective function
  with a given set of hyperparameters.

- Study: a collection of optimization trials where each
  trial uses hyperparameters sampled from a set of allowed values.

The set of hyperparameters for the trial which gives the optimal value for the
objective function are chosen as the best set of hyperparameters.

Scaling Optuna with Dask
------------------------

In this guide, you'll use Optuna to optimize several hyperparameters for an
XGBoost classifier trained on the
`breast cancer dataset <https://scikit-learn.org/stable/datasets/toy_dataset.html#breast-cancer-wisconsin-diagnostic-dataset>`_.
You'll also use `Dask-Optuna <https://jrbourbeau.github.io/dask-optuna>`_ and
`Joblib <https://joblib.readthedocs.io/en/latest/>`_ to run Optuna trials in
parallel on a Coiled cluster.

Click :download:`here <optuna-example.py>` to download this example.

.. literalinclude:: optuna-example.py

And with that, you're able to run distributed hyperparameter optimizations using
Optuna, Dask, and Coiled! For more details on using Optuna, Dask, and Coiled,
check out `this Coiled blog post <https://coiled.io/blog/scalable-hyperparameter-optimization-optuna-dask/>`_.
