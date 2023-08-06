import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="hgcal_utilities",
    version="1.0.3",
    description="Utilites to go with HGCROC-tools and Datenraffinerie",
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
    packages=["hgcal_utilities"],
    include_package_data=True,
    install_requires=[
                      "attrs",
                      "Babel",
                      "certifi",
                      "charset-normalizer",
                      "contextlib2",
                      "docutils",
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
                      "six",
                      "snowballstemmer",
                      "tomli",
                      "urllib3",
                      ],
    entry_points={
        "console_scripts": []
    },
)
