.. _gpus:

GPUs
====

Coiled supports running computations with GPU-enabled machines. You
can set ``worker_gpu=1`` when creating a Coiled cluster:

.. code-block:: python

   import coiled

   cluster = coiled.Cluster(
       ...,
       worker_gpu=1,
   )

Using GPUs requires some additional setup, though. The sections below will
walk you through how to set up and use Coiled with GPU-enabled machines.

Creating a software environment
-------------------------------

First, you will need a software environment that supports
GPU-accelerated libraries (e.g. PyTorch, RAPIDS, XGBoost, Numba),
and `CUDA Toolkit <https://developer.nvidia.com/cuda-toolkit>`_ version 11.
For example:

.. code-block:: python

   import coiled

   coiled.create_software_environment(
       name="gpu-test",
       container="gpuci/miniconda-cuda:11.2-runtime-ubuntu20.04",
       conda={
           "channels": [
               "rapidsai",
               "conda-forge",
               "defaults",
           ],
           "dependencies": [
               "coiled-runtime",
               "cupy",
               "cudatoolkit=11.2",
           ],
       },
   )

Creating a cluster
------------------

Next, you can create a cluster with GPU-enabled instance types. Currently,
Coiled only supports a single GPU per worker.

AWS
~~~

If you are using AWS, you can use the ``worker_vm_types`` keyword argument,
since GPU selection is tied to the instance type. Requesting a g4dn.xlarge
instance type, e.g., contains an NVIDIA T4 GPU.
We recommend the g4dn.xlarge (NVIDIA T4) or p3.2xlarge (NVIDIA V100) instance types.
For example:

.. code-block:: python

   import coiled

   cluster = coiled.Cluster(
       worker_vm_types=["g4dn.xlarge", "p3.2xlarge"],
       software="gpu-test",
   )

Since these recommended instance types have only one GPU, you do not need to
use the ``worker_gpu`` keyword argument. See the tutorial on :doc:`tutorials/select_gpu_type`.

.. attention::

    AWS users may run into availability issues and should confirm their
    region has the GPU instance type they have requested. See the `AWS
    documentation on EC2 instance types <https://aws.amazon.com/ec2/instance-types/>`_
    under the "Accelerated Computing".

Google Cloud
~~~~~~~~~~~~

If you are using Google Cloud, you can request GPUs using the
``worker_gpu`` (or ``worker_gpu_type``) and the ``worker_vm_types``
keyword arguments. You need both arguments since Google Cloud
adds GPUs to different instances (the one exception being 
A100, which is bundled with instance type a2-highgpu-1g).
See the `Google Cloud documentation on GPUs <https://cloud.google.com/compute/docs/gpus>`_
for more details.
You will also need to use an instance type from the
`N1 machine series <https://cloud.google.com/compute/docs/general-purpose-machines#n1_machines>`_.

If you specify ``worker_gpu=1`` and ``worker_vm_types=["n1-standard-2"]``, e.g.,
you will be requesting a single NVIDIA T4:

.. code-block:: python

   import coiled

   cluster = coiled.Cluster(
       worker_gpu=1,
       worker_vm_types=["n1-standard-2"],
       software="gpu-test",
   )

You can also specify a particular GPU with ``worker_gpu_type``:

.. code-block:: python

   import coiled

   cluster = coiled.Cluster(
       worker_gpu_type=["nvidia-tesla-v100"],
       worker_vm_types=["n1-standard-2"],
       software="gpu-test",
   )

See the tutorial on :doc:`tutorials/select_gpu_type`.

Testing
-------

You can test this cluster is working as expected with the following:

.. code-block:: python

    from dask.distributed import Client


    def test_gpu():
        import numpy as np
        import cupy as cp

        x = cp.arange(6).reshape(2, 3).astype("f")
        return cp.asnumpy(x.sum())


    client = Client(cluster)

    f = client.submit(test_gpu)
    f.result()

If successful, this should return ``array(15., dtype=float32)``.

You can also verify that workers are using GPUs with the following command:

.. code-block:: python

    cluster.scheduler_info["workers"]
