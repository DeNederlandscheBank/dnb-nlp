=============
solvency2-nlp
=============

.. image:: https://img.shields.io/badge/License-MIT/X-blue.svg
        :target: https://github.com/DeNederlandscheBank/solvency2-nlp/blob/master/LICENSE
        :alt: License

Experimental natural language processing projects with Solvency 2 documents

In this repository we publish our progress with respect to the application of natural language processing with Solvency 2 documents.

Installation
============

Clone the project::

    git clone https://github.com/DeNederlandscheBank/solvency2-nlp.git

Then start with a clean environment::
    
    conda create -n your_env_name python=3.6

And activate the environment::

    conda activate your_env_name

Install the required packages::

    pip install -r requirements.txt

This installs the packages for natural language processing that we use (scipy, gensim, nltk and lexnlp).

Install data
============

The cloned project does not contain any data, but code is included to download the data easily.

Legislation data
----------------

To get the legislation data, run in the project root::
    
    python src/data/make_law_data.py

Then you can choose from all official European languages.

You can also run::

    python src/data/make_law_data.py --language EN

to get the English version of the legislation. To get all languages use ``--language ALL``.

The data is downloaded from the eur-lex website (https://eur-lex.europa.eu/homepage.html). Currently, the following European legislation is downloaded:

* EU Delegated Regulation 2015/35 (Solvency 2)

On default, the pdf-documents are put in ``/data/external/law``.

The pdf-documents are processed (text from pdf is extracted with pdfminer.six and page headers are deleted) and the txt-files are put in ``/data/interim/law`` for further processing.

SFCR data
---------

To get the SFCR data, run in the project root::
    
    python src/data/make_sfcr_data.py

This downloads all the SFCRs defined in ``/data/metadata_sfcr.csv`` (the cvs-files contains the urls of the SFCR documents of a number of insurance undertakings).

The pdf-documents are processed and the txt-files are put in ``/data/interim/sfcr`` for further processing.

Project Organization
--------------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   │   ├── sfcr       <- PDF documents with Solvency and Financial Condition Reports of insurance undertakings
    │   │   └── law        <- PDF documents with Legislative texts
    │   ├── interim        <- Intermediate data that has been transformed.
    │   │   ├── sfcr       <- TXT files with Solvency and Financial Condition Reports of insurance undertakings
    │   │   └── law        <- TXT files with Ligislative texts
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- Documentation
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    │
    ├── src                <- Source code for use in this project
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download and process data
    │   │
    │   ├── nlp            <- Scripts to analyze text
    │   │
    │   ├── models         <- Scripts to train models and use results
    │   │
    │   └── visualization  <- Scripts to create visualizations
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
