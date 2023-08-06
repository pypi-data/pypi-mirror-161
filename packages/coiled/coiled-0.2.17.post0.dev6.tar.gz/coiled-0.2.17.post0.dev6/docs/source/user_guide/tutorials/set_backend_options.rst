======================================
Setting Backend Options via Python API
======================================

This article will show you how you can use the Python API to set backend
options.

Coiled allows users to configure the cloud computing resources they wish
to use (their "backend") via the :meth:`coiled.set_backend_options` command. This
command returns the current account username when invoked
and controls backend settings via keyword arguments.  Backend options,
when changed via the Python api will be reflected in the Coiled Cloud
UI, and will persist until changed again via the UI or via
``coiled.set_backend_options()``.

Using coiled.set_backend_options
--------------------------------

This function is fully documented in the :doc:`../api` section
of the Coiled documentation; this tutorial provides some example usage as a
supplement to that.

Currently, you can use this command to set your backend so Coiled creates resources in:

- Your AWS account
- Your Google Cloud Platform (GCP) account

Using your AWS account
^^^^^^^^^^^^^^^^^^^^^^

Let's assume you want to run Coiled in your AWs account, you can do such by running
the following command:


.. code:: python

    coiled.set_backend_options(
        backend="aws",
        aws_access_key_id="#-your-access-key-ID#",
        aws_secret_access_key="######-your-aws-secret-access-key-######",
    )

Note that by default, this command will chose ``us-east-1`` as your regions. You can use
the ``aws_region`` parameter to select a different region. For example:

.. code:: python

    coiled.set_backend_options(
        backend="aws",
        aws_access_key_id="#-your-access-key-ID#",
        aws_secret_access_key="######-your-aws-secret-access-key-######",
        aws_region="eu-west-2",
    )

Using your GCP account
^^^^^^^^^^^^^^^^^^^^^^

If you want to use Coiled in your Google Cloud Platform, the easiest way is to use
the path of the json file of your service account (obtained from following the  :doc:`../gcp_configure` docs).

.. code:: python

    coiled.set_backend_options(
        backend="gcp", gcp_service_creds_file="/path/to/your/gcp-service-account-creds.json"
    )

Alternatively, you can use the ``gcp_service_creds_dict`` if you wish to pass the
credentials as a dictionary instead.


Additional settings
-------------------

Regions
^^^^^^^

Other settings can be changed via ``coiled.set_backend_options``. For instance,
AWS regions can also be set:

.. code:: python

    coiled.set_backend_options(aws_region="us-west-1")

For a list of supported regions, see the :doc:`../aws_reference`.

Container Registries
^^^^^^^^^^^^^^^^^^^^

It is also possible to specify a Docker registry for your software
environments. For example, to use Docker Hub:

.. code:: python

    coiled.set_backend_options(
        registry_type="docker_hub",
        registry_uri="docker.io",
        registry_username="your-registry-username",
        registry_access_token="#######-registry-access-token-######",
    )

In using the preceding, keep in mind default Python behavior, which will reset
keyword arguments ``backend='aws'``, ``registry_type='ecr'``,
``aws_region='us-east-1'`` and ``registry_uri='docker.io'`` if they are not
explicitly included in the call.  So, if the goal is to use a user specified
Docker Hub container registry while working in GCP, that keyword argument must
also be set:

.. code:: python

    coiled.set_backend_options(
        backend="gcp",
        registry_type="docker_hub",
        registry_username="your-registry-username",
        registry_access_token="#######-registry-access-token-######",
    )

Networking
^^^^^^^^^^

.. note::

  This feature is available to all cloud providers that Coiled supports.

You can configure custom networking options when Coiled is configured to run in
your own AWS account. This allows you to customize the security group ingress
rules for resources that Coiled creates in your cloud provider account. 
For example, you have fine-grain control over the security
group by specifying which ports and CIDR block to use when Coiled creates a
security group.:

.. code:: python

    coiled.set_backend_options(
        backend="aws",
        aws_access_key_id="<your-access-key-id-here>",
        aws_secret_access_key="<your-access-key-secret-here>",
        customer_hosted=True,
        ingress=[{"ports": [100, 8754], "cidr": "10.0.5.1/16"}],
    )

For more details on AWS networking, refer to the networking section of the
:doc:`../aws_reference`
