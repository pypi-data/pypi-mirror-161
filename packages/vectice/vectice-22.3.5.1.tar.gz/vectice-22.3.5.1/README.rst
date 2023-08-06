Vectice SDK: Data Science Knowledge Auto-captured, for teams
============================================================

Enabling all enterprise’s AI/ML initiatives to result in consistent and positive impact. Data scientists deserve a solution that makes all their experiment reproducible, every asset discoverable and simplifies knowledge transfer. Managers deserve a dedicated data science solution. to secure knowledge, automate reporting and simplify reviews and processes.

.. contents:: Contents
    :depth: 2
    :local:

Supported Python Versions
^^^^^^^^^^^^^^^^^^^^^^^^^

Python >= 3.7.1

Documentation
^^^^^^^^^^^^^

Official documentation for Vectice can be found at `https://doc.vectice.com <https://doc.vectice.com/index.html>`_

Installing
^^^^^^^^^^
To install Vectice without any extras and get started. The following code snippet can be used.

 .. code-block:: python

    pip install vectice

To install Vectice with any extras and get started. The following code snippet can be used. All the provided extras can be found in the `documentation <https://doc.vectice.com/integration/index.html>`_.


 .. code-block:: python

    pip install vectice[extra_required]


Getting Started
^^^^^^^^^^^^^^^

The following code is just an example to test that the Vectice SDK is working as it should be. You can use an IDE or a notebook to execute this code. It's intializing a vectice object that connects to vectice. If everything is working as it should be you'll recieve no errors.


 .. code-block:: python

    from vectice import Vectice
    Vectice = Vectice("Team Workspace 1", "Project 1")

The Vectice SDK leverages runs as the terminology used when capturing metadata from the work you do. Thus, if you want to clean data, for example, and capture what you've done, you would create the inputs of the data that will be cleaned, create a run and then start it. Then you'd perform the data cleaning.

 .. code-block:: python

    from vectice import Experiment
    experiment = Experiment("My Job", "Project 1", "Team Workspace 1", job_type=JobType.PREPARATION)
    experiment.use_dataset_version(dataset="DATASET_NAME_IN_VECTICE_APP")
    experiment.start()

Once you've performed the data cleaning or any other actions you end the run by simple creating outputs and then calling the complete method.

 .. code-block:: python

    experiment.add_dataset_version(dataset="DATASET_NAME_IN_VECTICE_APP",...)
    vectice.complete()


Auto versioning
^^^^^^^^^^^^^^^

The Vectice SDK enables you to leverage auto versioning for a variety of artifacts such as datasets, models and code. Below is an example of auto versioning your code, to find out more see `code auto versioning <https://doc.vectice.com/howtos/auto_code.html>`_.


 .. code-block:: python

    experiment = Experiment("My Job", "Project 1", "Team Workspace 1", auto_code=True)
    experiment.start()
    experiment.complete()

Integrations
^^^^^^^^^^^^

Vectice integrates with popular data science tools. There are already a few integrations and MLflow is just one example and the roadmap has more exciting integrations on the way. If you would like to see more, please refer to the `integrations <https://doc.vectice.com/integration/index.html>`_ in the documentation

MLflow
^^^^^^

The integration of MLflow with Vectice uses the Python context manager to easily leverage MLflow with the Vectice API. The MLflow metadata is leveraged by the Vectice API and autolog allows all the metadata to be captured. Furthermore, more parameters and metrics can be captured by using MLflow methods.

 .. code-block:: python

    mlflow.autolog()
    experiment = Experiment("My Job", "Project 1", "Team Workspace 1", auto_code=True, lib=MLFlowClient())

    with experiment.start():
        mlflow.log_param("algorithm", "linear regression")
        mlflow.log_metric("MAE", MAE)


Examples
^^^^^^^^

There is an examples repository dedicated to providing examples of how to leverage the Vectice SDK and Vectice App, you will find integration examples and ways to leverage Vectice in a standalone approach. This can be found in the `vectice-examples repository <https://github.com/vectice/vectice-examples>`_.