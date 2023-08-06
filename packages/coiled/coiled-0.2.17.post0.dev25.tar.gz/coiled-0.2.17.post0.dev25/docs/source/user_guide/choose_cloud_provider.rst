Need a cloud provider account?
==============================

Coiled creates and manages Dask clusters in your own cloud provider account.
You don't need to know much about the cloud to use Coiled, but you do need a cloud provider account.

.. panels::
   :card: border-0
   :container: container-lg pb-3
   :column: col-md-6 col-md-6 p-2
   :body: text-center border-0
   :header: text-center border-0 h4 bg-white
   :footer: border-0 bg-white

   .. figure:: images/logo-aws.png
      :width: 35%
      :alt: Sign up for Amazon Web Services (AWS)

   +++

   .. link-button:: https://aws.amazon.com/free
      :text: Sign up for AWS Free Tier
      :classes: btn-full btn-block stretched-link

   ---


   .. figure:: images/logo-gcp.png
      :width: 100%
      :alt: Sign up for Google Cloud Free Tier

   +++

   .. link-button:: https://cloud.google.com/free
      :text: Sign up for Google Cloud Free Tier
      :classes: btn-full btn-block stretched-link

We currently support Amazon Web Services (AWS) and Google Cloud (GCP). Both cloud providers make it easy to get started.
There's no cost for having an account and both have free-tier offerings for many services,
though you'll pay for the resources you use when you create Dask clusters.

Once you've created an AWS or Google Cloud account, we'll walk you through the process of giving Coiled access to
create and manage Dask clusters in your account.

If you would like to learn more about how to use Dask,
Coiled offers `live in-depth training <https://coiled.io/course/scaling-python-with-dask/>`_.
If you're not sure deploying Dask on the cloud is the right solution for you,
see the Dask documentation on other options for `deploying Dask clusters <https://docs.dask.org/en/stable/deploying.html>`_.


How do I choose?
----------------

Coiled offers the same (or equivalent) features on both AWS and Google Cloud, and both cloud providers offer fairly
similar features at fairly similar costs.

If you already have data (or plans to store data) in Amazon's S3 service (or some other AWS service),
we recommend using AWS for Coiled.

If you already have data (or plans to store data) in Google's BigQuery service or some other GCP service,
we recommend using Google Cloud for Coiled.

If you're starting from scratch, either should work well!
AWS is more mature and has data centers in more locations across the world. More people are familiar with AWS, but
many people think that Google Cloud has a more developer-friendly user experience.


Will this be expensive?
-----------------------

The cost from your cloud provider to run a cluster with 200 cores for a hour
(100 ``t3.medium`` instances on AWS or ``e2-standard-2`` instances on Google Cloud) is about $5.
You can use Coiled for up to 10,000 CPU-hours per month with no additional cost.

Cloud providers charge you to store and transmit data; you can reduce this cost by keeping your data with a single cloud provider and in the same region as your cluster.

Very large instances types and GPUs can quickly increase the cost per hour, but they can also bring down your total cost
by letting you process large workloads in much less time.

As always, we're happy to chat about your specific needs. Feel free to reach out to us at support@coiled.io.
