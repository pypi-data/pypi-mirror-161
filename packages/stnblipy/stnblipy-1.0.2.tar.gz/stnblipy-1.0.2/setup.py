
from setuptools import setup, find_packages

VERSION = '1.0.2' 
DESCRIPTION = 'Framework para rotinas de ETL'
LONG_DESCRIPTION = 'Framework para simplificar o desenvolvimento de rotinas python, especialmente rotinas de ETL'

# Setting up
setup(
        name="stnblipy", 
        version=VERSION,
        author="Secretaria do Tesouro Nacional",
        # author_email="",
        license="GPL v2",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            "sqlalchemy==1.4.15", 
            "cx-Oracle==7.1.3", 
            "multipledispatch==0.6.0 ", 
            "pandas==1.1.5", 
            "openpyxl==3.0.10" ], 
        keywords=['python', 'ETL', 'framework'],
        classifiers= [
            "Programming Language :: Python :: 3.7",
        ]
)

