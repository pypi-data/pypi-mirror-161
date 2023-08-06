from setuptools import setup, find_packages

VERSION = '0.0.7' 
DESCRIPTION = 'Reddit,Twitter,Scrapers'
LONG_DESCRIPTION = 'First set of Reddit,Twitter Scrapers being uploaded as a package'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="rt_sports_scrapers", 
        version=VERSION,
        author="Mathew Mammen Jacob",
        author_email="<mathew.mammenjacob@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=['rt_sports_scrapers'],
        install_requires=['gspread','gspread_dataframe','twint-fork'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package','Scrappers'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)