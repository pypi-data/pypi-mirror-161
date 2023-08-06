from setuptools import setup, find_packages

VERSION = '0.1' 
DESCRIPTION = 'Basic Preprocessor for NLP '
LONG_DESCRIPTION = 'Set of preprocessing functions for nlp projects'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="NLPreprocessor", 
        version=VERSION,
        author="Mathew Mammen Jacob",
        author_email="<mathew.mammenjacob@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=['NLPreprocessor'],
        install_requires=['NLTK'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'Second package','NLP'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)