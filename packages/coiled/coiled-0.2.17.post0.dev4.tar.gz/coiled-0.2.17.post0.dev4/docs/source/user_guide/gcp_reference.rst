Google Cloud Platform (GCP)
===========================

IAM custom role
---------------

Coiled requires a limited set of IAM permissions to provision
infrastructure and compute resources in your GCP account.
See the :ref:`guide on configuring Google Cloud <gcp-iam-role>` for more information.

.. dropdown:: IAM custom role
   :title: bg-white

   Save the below YAML to a file on your local machine called ``coiled.yaml``:
   
   .. literalinclude:: ../../../../backends/policy/gcp-required-custom-role.yaml
      :language: yaml

.. _gcp-quotas:

Quotas
------

Each Google Cloud resource type has pre-defined quotas, which are the maximum number of resources you can create for a given resource type. You can view existing quotas and request increases from your `Google Cloud console <https://console.cloud.google.com/iam-admin/quotas>`_. If you have received error messages such as ``Quota <resource-type> exceeded``, you may want to request an increase. In particular, the following resource types often have insufficient quotas:

- **Persistent disk SSD (GB)** (see the Google Cloud documentation on `Disk quotas <https://cloud.google.com/compute/quotas#disk_quota>`_). You may need to request an increase if you see the ``Quota 'SSD_TOTAL_GB' exceeded`` error message.
- **In-use external IP addresses** (see the Google Cloud documentation on `External IP addresses <https://cloud.google.com/compute/quotas#external_ip_addresses>`_). You may need to request an increase if you see the ``Quota 'IN_USE_ADDRESSES' exceeded`` error message.
- **CPU** (see the Google Cloud documentation on `CPU quota <https://cloud.google.com/compute/quotas#cpu_quota>`_). You may need to request an increase if you see the ``Quota 'CPUS' exceeded`` error message.

.. _gcp_backend_options:

Backend options
---------------

There are several GCP-specific options that you can specify (listed below) to
customize Coiled’s behavior.

.. list-table::
   :widths: 25 50 25
   :header-rows: 1

   * - Name
     - Description
     - Default
   * - ``region_name``
     - GCP region to create resources in
     - ``us-east1``
   * - ``zone_name``
     - GCP zone to create resources in
     - ``us-east1-c``
   * - ``preemptible``
     - Whether or not to use preemptible instances for cluster workers
     - ``False``
   * - ``firewall``
     - Ports and CIDR block for the security groups that Coiled creates
     - ``{"ports": [22, 8787, 8786], "cidr": "0.0.0.0/0"}``

.. _gcp-backend-example:

You can specify backend options directly in Python:

.. code-block:: python

    import coiled

    cluster = coiled.Cluster(
        backend_options={"region_name": "us-central1", "preemptible": False}
    )

Or save them to your :ref:`Coiled configuration file <configuration>`:

.. code-block:: yaml

    # ~/.config/dask/coiled.yaml

    coiled:
      backend-options:
        region_name: us-central1

GPU support
-----------

Coiled supports running computations with GPU-enabled machines if your
account has access to GPUs. See the :doc:`GPU best practices <gpu>`
documentation for more information on using GPUs with GCP.

.. _logs-gcp:

Coiled logs
-----------

If you are running Coiled on your GCP account, cluster logs will be saved within
your GCP account. Coiled will send logs to 
`GCP Logging <https://cloud.google.com/logging/>`_ and
`GCP BigQuery <https://cloud.google.com/bigquery/>`_ 
(if BigQuery is enabled in the project).

We send logs to GCP Logging so that you can easily view logs with GCP Logs Explorer,
and we use GCP Cloud Storage/GCP BigQuery to back the logs views we display on the
`Cluster Dashboard <https://cloud.coiled.io/>`_.

.. note::

   Coiled will only use BigQuery if you have BigQuery enabled in your project and if
   you have the following permissions in your service account: ``bigquery.datasets.create``,
   ``bigquery.datasets.get``, ``bigquery.datasets.update`` and ``bigquery.jobs.create``

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Log Storage
     - Storage time
   * - ``GCP Logging``
     - 30 days
   * - ``GCP Cloud Storage (Coiled v1)``
     - 90 days
   * - ``GCP BigQuery dataset (Coiled v2)``
     - 10 days

When you configure your backend to use GCP, Coiled creates a bucket
named ``coiled-logs`` GCP Logging.

Networking
----------

When Coiled is configured to run in your own GCP account, you can customize the
firewall ingress rules for resources that Coiled creates in your GCP
account.

By default, Dask schedulers created by Coiled will be reachable via ports
8787 and 8786 from any source network. This is consistent with the default
ingress rules that Coiled configures for its GCP firewalls:

.. list-table::
   :widths: 25 25 50
   :header-rows: 1

   * - Protocol
     - Port
     - Source
   * - tcp
     - 8787
     - ``0.0.0.0/0``
   * - tcp
     - 8786
     - ``0.0.0.0/0``
   * - tcp
     - 22
     - ``0.0.0.0/0``

.. note::
    Ports 8787 and 8786 are used by the Dask dashboard and Dask protocol respectively.
    Port 22 optionally supports incoming SSH connections to the virtual machine.

Configuring firewall rules
^^^^^^^^^^^^^^^^^^^^^^^^^^

While allowing incoming connections on the default Dask ports from any source
network is convenient, you might want to configure additional security measures
by restricting incoming connections. This can be done by using
:meth:`coiled.set_backend_options` or by using the ``backend_options``.
