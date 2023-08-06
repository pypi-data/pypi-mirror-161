from setuptools import setup, find_packages
#from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
# Setting up
setup(
       # the name must match the folder name 'kdslib'
        name="kdslib", 
        version='1.0.5',
        author="kdslibraries",
        author_email="kdslibraries@aol.com",
        description='KDS logging and data connection helpers',
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=find_packages(),
        install_requires=['msal','requests','sqlalchemy','teradata','teradatasql','pymssql','teradatasqlalchemy'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'msal'
        
        keywords=['python', 'kdslib'],
        classifiers= [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)