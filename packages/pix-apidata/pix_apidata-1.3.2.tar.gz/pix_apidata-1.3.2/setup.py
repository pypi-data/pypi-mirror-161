import pathlib
from setuptools import setup ,find_packages
from os import path
# The directory containing this file
#HERE = pathlib.Path(__file__).parent

# The text of the README file
#README = (HERE / "README.md").read_text()
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    README = f.read()

# This call to setup() does all the work
setup(
    name="pix_apidata",
    version="1.3.2",
    author="Coumar Pandourangane",
    author_email="pscoumar@gmail.com",
    description="Python library to connect and stream the market data.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/pscoumar",
    license="MIT",
    classifiers=[ 
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    keywords = 'stock market, apidata, accelpix, ticanalytics',
    packages=['pix_apidata'],
    include_package_data=True,
    install_requires=['signalrcore-async', 'urllib3'],

)
