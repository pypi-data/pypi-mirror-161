import setuptools
import os
import re

with open("README.md", "r") as fh:
    long_description = fh.read()

PACKAGE_NAME = 'dayfilter'
current_path = os.path.abspath(os.path.dirname(__file__))
version_line = open(os.path.join(current_path, PACKAGE_NAME, 'version.py'), "rt").read()

m = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_line, re.M)
__version__ = m.group(1)

setuptools.setup(
    name = PACKAGE_NAME,
    version = __version__, # versions '0.0.x' are unstable and subject to refactor
    author = "Muhammad Yasirroni",
    author_email = "muhammadyasirroni@gmail.com",
    description = "Filter time-series based on sun movement",
    long_description = long_description,
    url = f"https://github.com/yasirroni/{PACKAGE_NAME}",
    long_description_content_type = "text/markdown",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires = '>3.6',
    install_requires = [
        "pytz>=2020.1"
    ],
)
