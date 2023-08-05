Amazon Web Services (AWS)
=========================

IAM Policies
------------

Coiled requires a limited set of IAM permissions to provision
infrastructure and compute resources in your AWS account.
See the :ref:`guide for configuring AWS <aws-iam-policy>` for more information.

.. dropdown:: AWS IAM Setup policy document (JSON)

  .. literalinclude:: ../../../../backends/policy/aws-required-policy-setup.json
    :language: json

.. dropdown:: AWS IAM Ongoing policy document (JSON)

  .. literalinclude:: ../../../../backends/policy/aws-required-policy-ongoing.json
    :language: json

Resources
---------

When you create a Dask cluster with Coiled on your own AWS account, Coiled will
provision the following resources on your AWS account:

.. figure:: images/backend-coiled-aws-architecture.png
   :width: 90%

   AWS resources for a Dask cluster with 5 workers

When you create additional Dask clusters with Coiled, then another scheduler VM
and additional worker VMs will be provisioned within the same public and private
subnets, respectively. As you create additional Dask clusters, Coiled will reuse
and share the existing VPC and other existing network resources that were
initially created.

.. warning::
   If you get a permissions error when reading from an S3 bucket,
   you may need to attach S3 policies to the role that Coiled creates to
   attach to EC2 instances. The role name is the same as your account slug.

.. seealso::

  If you encounter any issues when setting up resources, you can use the method
  :meth:`coiled.get_notifications` to have more visibility into this process.
  You might also be interested in reading our
  :doc:`Troubleshooting guide <troubleshooting/visibility_resource_creation>`.

.. seealso::

  You might be interested in reading the tutorial on
  :doc:`How to limit Coiled's access to your AWS resources <tutorials/aws_permissions>`.

  You might be interested in reading the tutorial on
  :doc:`Managing resources created by Coiled <tutorials/resources_created_by_coiled>`.

.. _aws-quotas:

Quotas
------

Each AWS service has pre-defined quotas, or limits, which are the maximum values for the resources in your AWS account (see the `AWS Service Quotas guide <https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html>`_). You may want to request an increase in these quotas, especially if you have received ``LimitExceeded`` error messages while using Coiled. You can view the default quotas or request an increase from the `Service Quotas console <https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas>`_. You can follow `these instructions from AWS Support <https://aws.amazon.com/premiumsupport/knowledge-center/ec2-on-demand-instance-vcpu-increase/>`_ to request an increase.

.. _aws_backend_options:

Backend Options
---------------

There are several AWS-specific options that you can specify (listed below) to
customize Coiled's behavior. Additionally, the next section contains an example
of how to configure these options in practice.

.. list-table::
   :widths: 25 50 25
   :header-rows: 1

   * - Name
     - Description
     - Default
   * - ``region_name``
     - AWS region to create resources in
     - ``us-east-1``
   * - ``zone_name``
     - AWS Availability Zone to create cluster
     - depends on region
   * - ``spot``
     - Whether or not to use spot instances for cluster workers
     - ``False``
   * - ``firewall``
     - Ports and CIDR block for the security groups that Coiled creates
     - ``{"ports": [22, 8787, 8786], "cidr": "0.0.0.0/0"}``


The currently supported AWS regions are:

* ``us-east-1``
* ``us-east-2``
* ``us-west-1``
* ``us-west-2``
* ``ap-southeast-1``
* ``ca-central-1``
* ``ap-northeast-1``
* ``ap-northeast-2``
* ``ap-south-1``
* ``ap-southeast-1``
* ``ap-southeast-2``
* ``eu-central-1``
* ``eu-north-1``
* ``eu-west-1``
* ``eu-west-2``
* ``eu-west-3``
* ``sa-east-1``

.. note::

  Coiled will choose the ``us-east-1`` region by default. If you don't
  wish to use this region, you should provide a different region.

.. _aws-backend-example:

You can specify backend options directly in Python:

.. code-block:: python

    import coiled

    cluster = coiled.Cluster(backend_options={"region_name": "us-west-1"})

Or save them to your :ref:`Coiled configuration file <configuration>`:

.. code-block:: yaml

    # ~/.config/dask/coiled.yaml

    coiled:
      backend-options:
        region: us-west-1

GPU support
-----------

This backend allows you to run computations with GPU-enabled machines if your
account has access to GPUs. See the :doc:`GPU best practices <gpu>`
documentation for more information on using GPUs with this backend.

Workers currently have access to a single GPU, if you try to create a cluster
with more than one GPU, the cluster will not start, and an error will be
returned.

.. _logs-aws:

Coiled logs
-----------

If you are running Coiled on your own AWS account, cluster logs will be saved
within your AWS account. Coiled will use
`CloudWatch <https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html>`_
to store logs.

Coiled will create a log group with your account name and add a log stream for
each instances that Coiled creates. These logs will be stored for 30 days.

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Log Storage
     - Storage time
   * - ``Cloudwatch``
     - 30 days


Availability Zone
-----------------

The availability of different VM instance types varies across AZs, so choosing a different AZ may make it easier to create a cluster with the desired number and type of instances.

This option allows you to pick the `Availability Zone <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-availability-zones>`_ (AZ) to use for a cluster. Each AZ is one or more distinct data centers located within a region. For example, the ``us-east-1`` region contains the ``us-east-1a`` zone, (as well as ``b``, ``c``, ``d``, and ``f`` zones).

You can specify the zone to use when creating an individual cluster like so:

.. code-block:: python

    cluster = coiled.Cluster(backend_options={"zone_name": "us-east-1b"})

In order to create a Dask cluster in a given AZ, we need a subnet for that specific zone.

When you configure Coiled to use your AWS account (as described :ref:`above <aws configure account backend>`), Coiled attempts to create a subnet for every zone in the selected region instead of just the default zone (note that there are no additional AWS or Coiled costs associated with each subnet).

When creating a Dask cluster, you can specify the zone to use for that cluster. Ideally the specified zone already has the required subnet (created when you configured Coiled to use your AWS account) but if not, we'll attempt to create a subnet at cluster-creation time. This may fail if Coiled no longer has "setup" IAM permissions; you'll get an error message if we are unable to find or create a subnet in the specified zone.

Assuming we are able to find or create the required subnet, then we'll then create your Coiled cluster in the specified availability zone.

If no zone is specified when creating an individual cluster, we'll use the ``zone`` set at the account level (currently this can only be set if you configure your account backend using the the Python API), and if that isn't set, we'll use the default zone for the region your account is configured to use.

Refer to the AWS documentation on `Regions and Availability Zones <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html>`_ for additional information.

Networking
----------

When Coiled is configured to run in your own AWS account, you can customize the
security group ingress rules for resources that Coiled creates in your AWS
account.

By default, Dask schedulers created by Coiled will be reachable via ports 22,
8787 and 8786 from any source network. This is consistent with the default
ingress rules that Coiled configures for its AWS security groups:

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
