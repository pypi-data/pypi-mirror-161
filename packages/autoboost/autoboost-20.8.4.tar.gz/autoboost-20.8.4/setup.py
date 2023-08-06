"""setup file for the project."""
# code gratefully take from https://github.com/navdeep-G/setup.py

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os

from setuptools import find_packages, setup
from autoboost import __version__

# Package meta-data.
NAME = 'autoboost'
DESCRIPTION = \
    'A thin wrapper for step-wise parameter optimization of boosting algorithms.'

URL_GITHUB = "https://github.com/gieses/autoboost"
URL_ISSUES = "https://github.com/gieses/autoboost/issues"
EMAIL = 'sven.giese88@gmail.com'
REQUIRES_PYTHON = '>=3.9'
KEYWORDS = ["xgboost", "lightgbm", "sklearn", "optimization"]
# What packages are required for this module to be executed?
REQUIRED = ['xgboost', 'lightgbm', 'scikit-learn', 'seaborn', 'matplotlib', 'numpy', 'tqdm']

AUTHOR = "Sven H. Giese"
# What packages are optional?
EXTRAS = {}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's _version.py module as a dictionary.
about = {}
project_slug = "autoboost"

# Where the magic happens:
setup(
    name=NAME,
    version=__version__,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    project_urls={
        "Bug Tracker": URL_ISSUES,
        "Source Code": URL_GITHUB,
        # "Documentation": URL_DOKU,
        # "Homepage": URL,
        # "Related Software": DACS_SOFTWARE},
    },
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*", "tests.*.*"]),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    # license='BSD 3-Clause',
    keywords=KEYWORDS,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
