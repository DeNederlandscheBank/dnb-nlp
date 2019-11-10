=============
solvency2-nlp
=============

.. image:: https://img.shields.io/badge/License-MIT/X-blue.svg
        :target: https://github.com/DeNederlandscheBank/solvency2-nlp/blob/master/LICENSE
        :alt: License

Experimental natural language processing projects with Solvency 2 documents

In this repository we publish our progress in natural language processing with Solvency 2 documents.

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

Credits
-------

This package was created with Cookiecutter and the data science project template (https://drivendata.github.io/cookiecutter-data-science).
