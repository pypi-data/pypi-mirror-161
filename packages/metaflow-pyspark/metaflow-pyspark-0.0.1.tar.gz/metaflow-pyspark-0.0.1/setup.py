from setuptools import setup, find_namespace_packages

version = "0.0.1"

setup(
    name="metaflow-pyspark",
    version=version,
    description="An EXPERIMENTAL PySpark decorator for Metaflow",
    long_description="Join `Metaflow support Slack <http://slack.outerbounds.co>`_ if you want to give this package a try.",
    author="Ville Tuulos",
    author_email="ville@outerbounds.co",
    packages=find_namespace_packages(include=["metaflow_extensions.*"]),
    py_modules=[
        "metaflow_extensions",
    ],
    install_requires=[
         "metaflow"
    ]
)
