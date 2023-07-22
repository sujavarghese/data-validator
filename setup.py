from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='file-validator',
    version='0.1.0',

    description='File Validator and Analyzer',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/jbadigital/file-validator',

    author='Suja Varghese',
    author_email='suja.varghese@kalido.com.au',
    scripts=['file_validator/__main__.py'],
    install_requires=[
        'pandas==0.23.4',
        'csvvalidator==1.2',
        'xmlschema==1.0.7',
        'sqlalchemy==1.3.0',
        "openpyxl==2.6.2",
        "pdfkit==0.6.1",
    ],
)
