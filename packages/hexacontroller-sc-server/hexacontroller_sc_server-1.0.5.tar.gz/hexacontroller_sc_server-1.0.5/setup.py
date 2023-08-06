import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="hexacontroller_sc_server",
    version="1.0.5",
    description="A prospective zmq-i2c server replacement",
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
    packages=["hexacontroller_sc_server"],
    include_package_data=True,
    install_requires=[
                      "alabaster",
                      "attrs",
                      "Babel",
                      "certifi",
                      "charset-normalizer",
                      "click",
                      "contextlib2",
                      "docutils",
                      "gpiod",
                      "guzzle-sphinx-theme",
                      "hgcal_utilities",
                      "idna",
                      "imagesize",
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
                      "smbus2",
                      "snowballstemmer",
                      "Sphinx",
                      "sphinxcontrib-applehelp",
                      "sphinxcontrib-devhelp",
                      "sphinxcontrib-htmlhelp",
                      "sphinxcontrib-jsmath",
                      "sphinxcontrib-qthelp",
                      "sphinxcontrib-serializinghtml",
                      "tomli",
                      "urllib3",
                      "zmq"
                      ],
    entry_points={
        "console_scripts": [
            "hexacontroller_sc_server=hexacontroller_sc_server.__main__:run_server",
        ]
    },
)
