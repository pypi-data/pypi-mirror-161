====================================
Managing resources created by Coiled
====================================

When using Coiled in your AWS account, you might want to know if Coiled created a
resource. Most of the resources that Coiled creates in your AWS account will be
tagged (see :ref:`Tags <cluster-tags>`). You search for Coiled-related tags using the 
`AWS Resource Groups Tag Editor <https://docs.aws.amazon.com/ARG/latest/userguide/find-resources-to-tag.html>`_

If you use the AWS resource groups tag editor, make sure you select 
"All supported resource types" from the Resource types dropdown. This
tool will search for all the resources that share the same tag key. 

You can use ``Name`` as tag and type ``coiled`` in the value input to
get a list of all resources that have Coiled in their tags.

.. figure:: ../images/aws-tag-editor.png
    :width: 100%

Alternatively, you can use ``boto3`` (the AWS SDK for Python)
to search for a list of resources that were created by Coiled.
See the `Boto3 documentation <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/resourcegroupstaggingapi.html>`_ on the ``ResourceGroupsTaggingAPI``.

.. code:: python

  import boto3

  client = boto3.client("resourcegroupstaggingapi")
  response = client.get_resources(
      TagFilters=[
          {"Key": "owner", "Values": ["coiled"]},
          {
              "Key": "Name",
              "Values": [
                  "coiled-vm-network-network",
                  "coiled-vm-network-priv-subnet",
                  "coiled-vm-network-pub-subnet",
                  "cloudbridge-inetgateway",
              ],
          },
      ]
  )
  print(response)

If you get an empty list, you might need to use fewer tags on each request to ``get_resources``.
