# coding: utf-8

from setuptools import setup, find_packages
from os import path

NAME = "groupdocs-rewriter-cloud"
VERSION = "22.8"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "pyopenssl", "urllib3[secure]", "python-dateutil",
            "requests[security]"]

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description='GroupDocs.Rewriter Cloud SDK',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Aspose',
    author_email='ekaterina.tretiak@aspose.com',
    url="https://github.com/groupdocs-rewriter-cloud/groupdocs-rewriter-cloud-python",
    license='MIT',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    keywords=["GroupDocs.Rewriter Cloud API Reference", "Aspose", "GroupDocs", "Rewriter" "Rewriter Cloud"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True
    # long_description="""
    # GroupDocs.Rewriter Cloud API Reference
    # This package contains GroupDocs.Rewriter Cloud SDK for Python.
    # This SDK allows you to work with GroupDocs.Rewriter Cloud REST APIs in your Python applications, and integrate Rewriter functionality in few steps.
    #
    # In detail, it's a set of SDKs for plain text and document rewriting in our Cloud. It supports paraphrasing of Word and PDF documents. Just pass text or parameteres of document uploaded to our Cloud Storage, to the GroupDocs.Rewriter Cloud API, and it will return paraphrased text or will save paraphrased file in Cloud Storage usinng specified path and name.
    #
    # It is easy to get started with GroupDocs.Rewriter Cloud, and there is nothing to install locally or configure servers. Create an account at GrroupDocs Cloud and get your application KEY, import this python, module, initialize "Configuration. class with this keys, and then you are ready to use the API.
    # """
)
