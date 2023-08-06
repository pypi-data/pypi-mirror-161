from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Utilities to assist in coding'
LONG_DESCRIPTION = 'Utilities to assist in coding'

# Setting up
setup(
       # the name must match the folder name 'moldyutilities'
        name="moldyutilities", 
        version=VERSION,
        author="Eric Nuno",
        author_email="ericnuno@gmail.com",
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