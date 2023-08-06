import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="hgcroc_configuration_client",
    version="1.0.3",
    description="Client for communication with HGCROC-tools' ROC \
                configuration server",
    # long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/albecker/hgcroc-tools.git",
    author="Alex Becker, Jonathan Trieloff",
    author_email="j.trieloff@cern.ch",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["hgcroc_configuration_client"],
    include_package_data=True,
    install_requires=[
                      "attrs",
                      "Babel",
                      "certifi",
                      "charset-normalizer",
                      "contextlib2",
                      "hgcal_utilities",
                      "idna",
                      "iniconfig",
                      "Jinja2",
                      "MarkupSafe",
                      "numpy",
                      "packaging",
                      "pandas",
                      "pathlib2",
                      "pluggy",
                      "py",
                      "Pygments",
                      "pyparsing",
                      "pytest",
                      "python-dateutil",
                      "pytz",
                      "PyYAML",
                      "pyzmq",
                      "requests",
                      "schema",
                      "six",
                      "snowballstemmer",
                      "tomli",
                      "urllib3",
                      "zmq"
                      ],
    entry_points={
        "console_scripts": []
    },
)
