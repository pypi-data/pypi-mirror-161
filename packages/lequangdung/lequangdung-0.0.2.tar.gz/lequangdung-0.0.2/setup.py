from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.2'
DESCRIPTION = 'Lê Quang Dũng 2007'
LONG_DESCRIPTION = 'Lê Quang Dũng 2007 Zalo 0985171149'

# Setting up
setup(
    name="lequangdung",
    version=VERSION,
    author="Le Quang Dung",
    author_email="<dunggdepptryy@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['lequangdung', 'lequangdung2007', 'lequangdung17092007', 'mail10plequangdung'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
