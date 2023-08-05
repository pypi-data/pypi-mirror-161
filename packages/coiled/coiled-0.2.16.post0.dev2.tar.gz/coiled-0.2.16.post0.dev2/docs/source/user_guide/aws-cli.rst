AWS Quickstart
~~~~~~~~~~~~~~

It's quick and easy to get started using Coiled in your own AWS account.
This guide will cover the steps for getting started with Coiled
using the command-line interface, all from your terminal.

#. Install the Coiled Python library with::

    pip install coiled

   **or**::

    conda install -c conda-forge coiled

#. Log in to your Coiled account::

    coiled login

#. Set up IAM::

    coiled setup aws

   With your permission, this command will create the IAM policies and infrastructure Coiled needs so you can create clusters in your AWS account. You will be prompted with an explanation at each step, so you can choose to say "yes" (or "no") at any point (see :doc:`aws_configure` for more details). 

   .. note::
      If you don't have an AWS account, you can sign up for `AWS Free Tier <https://aws.amazon.com/free>`_.

#. Start your Dask cluster in the cloud (see :ref:`Running your computation <first-computation>`)::

    ipython
    > import coiled
    > cluster = coiled.Cluster(n_workers=10)

If you don't already an AWS account and have more questions, see :ref:`Need a cloud provider account? <no-cloud-provider>`

Coiled makes it easy to deploy clusters in a way that's secure by default.
If you have questions about how we handle security, see our documentation about :doc:`security` (or talk to us!).
