Configuring AWS
===============

.. important::
    We recommend using the command-line setup option in the :doc:`aws-cli`. If this option does not work for you, then continue with the steps below to use the AWS console.

In this guide you will use the AWS console to configure Coiled to run Dask computations on your AWS account. You will first create an IAM user from your AWS acccount then configure your Coiled cloud account to use your AWS account.

Before you start
~~~~~~~~~~~~~~~~

This guide assumes you have already `created your Coiled account <https://cloud.coiled.io/signup>`_
and have an AWS account. If you don't have an AWS account, you can sign up for
`AWS Free Tier <https://aws.amazon.com/free>`_.

Create IAM user
~~~~~~~~~~~~~~~

First, you will create an IAM user in your AWS account. Watch the video below to follow along, then you can :ref:`configure your Coiled cloud account <aws configure account backend>`.

.. raw:: html

    <script src="https://fast.wistia.com/embed/medias/dr3yt1u88f.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><div class="wistia_responsive_padding" style="padding:56.25% 0 0 0;position:relative;"><div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%;"><div class="wistia_embed wistia_async_dr3yt1u88f videoFoam=true" style="height:100%;position:relative;width:100%"><div class="wistia_swatch" style="height:100%;left:0;opacity:0;overflow:hidden;position:absolute;top:0;transition:opacity 200ms;width:100%;"><img src="https://fast.wistia.com/embed/medias/dr3yt1u88f/swatch" style="filter:blur(5px);height:100%;object-fit:contain;width:100%;" alt="" aria-hidden="true" onload="this.parentNode.style.opacity=1;" /></div></div></div></div>

1. Sign in to the Console
^^^^^^^^^^^^^^^^^^^^^^^^^

Sign in to the `AWS console <https://console.aws.amazon.com>`_ (see `these instructions <https://docs.aws.amazon.com/IAM/latest/UserGuide/console.html#root-user-sign-in-page>`_ in the AWS documentation if you're having trouble).

.. _aws-iam-policy:

2. Create IAM policies
^^^^^^^^^^^^^^^^^^^^^^

Coiled requires a limited set of IAM permissions to provision
infrastructure and compute resources in your AWS account.
Follow the steps in the
`AWS user guide on how to create new IAM policies <https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_create-console.html#access_policies_create-json-editor>`_. 

We'll create two policies, one for initial setup and another for ongoing use.
When you arrive at the step to insert a JSON policy document, copy and paste
the following JSON policy documents. You can name them ``coiled-setup`` and ``coiled-ongoing``,
respectively, to make them easy to locate in the next step.

.. dropdown:: AWS IAM Setup policy document (JSON)

  .. literalinclude:: ../../../../backends/policy/aws-required-policy-setup.json
    :language: json

.. dropdown:: AWS IAM Ongoing policy document (JSON)

  .. literalinclude:: ../../../../backends/policy/aws-required-policy-ongoing.json
    :language: json

.. _aws-iam-user:

3. Create a new IAM user
^^^^^^^^^^^^^^^^^^^^^^^^

Follow the steps in the `AWS guide on creating a new IAM user <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console>`_. This IAM user must have `programmatic access <https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys>`_. Creating an IAM role with `temporary access keys <https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#temporary-access-keys>`_ will not be sufficient.

4. Attach IAM policies
^^^^^^^^^^^^^^^^^^^^^^

Now that you have created the two IAM policies with all necessary permissions,
you can attach these policies to the IAM user you created in step 2. Follow the steps in the
`AWS user guide on attaching IAM identity permissions <https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html#add-policies-console>`__.

5. Obtain AWS credentials
^^^^^^^^^^^^^^^^^^^^^^^^^

Coiled provisions resources on your AWS account through the use of AWS security
credentials. Select the user you created :ref:`previously <aws-iam-user>`. Follow the steps in the
`AWS user guide on programmatic access <https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys>`_
to obtain (or create) your access key ID and secret access key. They will resemble the
following:

.. code-block:: text

   Example AWS Secret Access ID: AKIAIOSFODNN7EXAMPLE
   Example AWS Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

Keep these credentials handy since you will configure them in Coiled Cloud
in the next step.

.. note::
    The AWS credentials you supply must be long-lived (not temporary) tokens.

.. _aws configure account backend:

Configure your Coiled cloud account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now you're ready to configure the cloud backend in your Coiled account to
use your AWS account.

Watch the video below to follow along:

.. raw:: html

    <script src="https://fast.wistia.com/embed/medias/fxf2cwk9gi.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><div class="wistia_responsive_padding" style="padding:56.25% 0 0 0;position:relative;"><div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%;"><div class="wistia_embed wistia_async_fxf2cwk9gi videoFoam=true" style="height:100%;position:relative;width:100%"><div class="wistia_swatch" style="height:100%;left:0;opacity:0;overflow:hidden;position:absolute;top:0;transition:opacity 200ms;width:100%;"><img src="https://fast.wistia.com/embed/medias/fxf2cwk9gi/swatch" style="filter:blur(5px);height:100%;object-fit:contain;width:100%;" alt="" aria-hidden="true" onload="this.parentNode.style.opacity=1;" /></div></div></div></div>

1. Log in to your Coiled account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, `log in to your Coiled account <https://cloud.coiled.io/login>`_.
In the navigation bar on the left, click on ``Setup``. Select
``Cloud Provider Configuration``, then click the ``Edit`` button:

.. figure:: images/cloud-backend-start.png
   :width: 100%

.. note::
   You can configure a different cloud backend for each Coiled account (i.e.,
   your personal/default account or your :doc:`Team account <teams>`). Be sure
   that you're configuring the correct account by switching accounts at the top
   of the left navigation bar in your Coiled dashboard if needed.

2. Select your cloud provider
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On the ``Select Your Cloud Provider`` step, select the ``AWS`` option, then
click the ``Next`` button:

.. figure:: images/cloud-backend-provider-aws.png
   :width: 100%

3. Configure AWS
^^^^^^^^^^^^^^^^

On the ``Configure AWS`` step, select your default AWS region
(i.e., when a region is not specified in the Coiled Python client).
Enter your ``AWS Access Key ID`` and ``AWS Secret Access Key``
from the previous step, then click the ``Next``:

.. figure:: images/cloud-backend-keys-aws.png
   :width: 100%

4. Network configuration
^^^^^^^^^^^^^^^^^^^^^^^^

On the ``Network Configuration`` step, select whether you would like
Coiled to automatically create new or manually use existing VPC and network resources
(see :doc:`tutorials/bring_your_own_network`):

.. figure:: images/cloud-backend-network.png
    :width: 100%

5. Container registry
^^^^^^^^^^^^^^^^^^^^^

On the ``Container Registry`` step, select whether you want to store Coiled
software environments in Amazon Elastic Container Registry (ECR), the default option,
or Docker Hub, then click ``Next``:

.. figure:: images/cloud-backend-registry-aws.png
   :width: 100%

6. Review
^^^^^^^^^

Review your cloud backend provider options, then click the ``Submit`` button:

.. figure:: images/cloud-backend-review-aws.png
   :width: 100%

On the next page, you will see the resources provisioned by Coiled in real time.

Next Steps
~~~~~~~~~~

Congratulations, Coiled is now configured to use your AWS account!

.. note::
   Now that you have completed these configuration steps, you can
   detach the ``coiled-setup`` policy to restrict Coiled to only
   use the IAM permissions defined in the ``coiled-ongoing`` policy.

Follow the :doc:`Getting Started tutorial <getting_started>` to create a Coiled
cluster and run a computation. When you create your first cluster,
Coiled will create a new VPC, subnets, AMI, EC2 instances,
and other resources on your AWS account that are used to power your Dask
clusters. See :doc:`aws_reference` for a more detailed description of these resources and additional configuration options.