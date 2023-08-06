import sys
import os
from setuptools import setup
from ast import parse

if sys.version_info < (3, 7):
    print("vectice requires Python 3 version >= 3.7", file=sys.stderr)
    sys.exit(1)

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.rst")

version_requires = ">=3.7.1"


with open(os.path.join("vectice", "__version__.py")) as f:
    __version__ = parse(next(filter(lambda line: line.startswith("__version__"), f))).body[0].value.s

with open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()
    readme.replace("Python >= 3.7.1", f"Python {version_requires}")

setup(
    name="vectice",
    version=__version__,
    description="Vectice Python library",
    long_description=readme,
    author="Vectice Inc.",
    author_email="sdk@vectice.com",
    url="https://www.vectice.com",
    packages=[
        "vectice",
        "vectice.api",
        "vectice.api.json",
        "vectice.models",
        "vectice.utils",
    ],
    package_data={"vectice": ["py.typed"]},
    license="Apache License 2.0",
    keywords=["Vectice", "Client", "API", "Adapter"],
    platforms=["Linux", "MacOS X", "Windows"],
    python_requires=version_requires,
    install_requires=[
        "requests >= 2.5.0",
        "urllib3",
        "python-dotenv >= 0.11.0",
    ],
    tests_require=["mock >= 1.0.1", "pytest", "coverage", "pytest-cov", "testcontainers"],
    extras_require={
        "dev": [
            "bandit",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
            "Pygments",
            "types-requests",
            "types-urllib3",
            "boto3-stubs[essential]",
        ],
        "mlflow": ["mlflow"],
        "doc": [
            "sphinx >=4.4.0,<=5.0.2",
            "recommonmark",
            "nbsphinx",
            "sphinx-rtd-theme >= 1.0.0",
            "pypandoc",
            "jupyterlab",
        ],
        "git": ["GitPython"],
        "github": ["PyGithub"],
        "bitbucket": ["atlassian-python-api"],
        "gitlab": ["python-gitlab"],
        "pandas": ["pandas"],
        "jupyter": ["jupyter_core", "ipykernel", "traitlets"],
        "collab": ["oauth2client", "GitPython >= 3.1.14"],
        "bigquery": ["google-cloud-bigquery >= 2.32.0", "google-cloud-bigquery-storage >= 2.11.0"],
        "gcs": ["google-cloud-storage >= 1.17.0"],
        "s3": ["boto3"],
    },
    classifiers=[
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
)
