from setuptools import setup, find_packages

VERSION = '0.0.5' 
DESCRIPTION = 'Patent Classification'
LONG_DESCRIPTION = 'Evaluate the accuracy of embeddings model based on Patent Classification performance'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="patent_classification", 
        version=VERSION,
        author="AI-Growth-Lab",
        author_email="hamidb@business.aau.dk",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)