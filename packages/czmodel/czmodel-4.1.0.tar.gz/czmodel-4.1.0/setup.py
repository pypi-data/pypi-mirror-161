# Copyright 2020 Carl Zeiss Microscopy GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Holds all relevant information for packaging and publishing to PyPI."""
import setuptools

# Exclude TF2.1 due to buggy behaviour
requirements = ["tensorflow>=2,<3,!=2.1", "onnx", "tf2onnx", "numpy", "xmltodict", "defusedxml"]

test_requirements = [
    "pytest",
    "pytest-cov",
    "pytest-timeout",
    "mypy",
    "types-all",
    "pylint_runner",
    "flake8",
    "flake8-docstrings",
    "flake8-bugbear",
    "bandit",
    "black",
]

dev_requirements = test_requirements.copy()

extra_requirements = {
    "test": test_requirements,
    "dev": dev_requirements,
    "all": [
        *requirements,
        *test_requirements,
        *dev_requirements,
    ],
}

VERSION = "4.1.0"

# pylint: disable=line-too-long
with open("README.md", "r", encoding="utf-8") as fh_read:
    long_description = fh_read.read()
setuptools.setup(
    name="czmodel",
    version=VERSION,
    entry_points={"console_scripts": ["savedmodel2czann=czmodel.convert:main"]},
    author="Sebastian Soyer",
    author_email="sebastian.soyer@zeiss.com",
    description="A conversion tool for TensorFlow or ONNX ANNs to CZANN",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Note: Exclude test folder in MANIFEST.in to also remove from source dist
    # See https://stackoverflow.com/questions/8556996/setuptools-troubles-excluding-packages-including-data-files
    # See https://docs.python.org/3.6/distutils/sourcedist.html
    packages=setuptools.find_packages(exclude=["test", "test.*"]),
    license_files=["LICENSE.txt", "NOTICE.txt"],
    # Classifiers help users find your project by categorizing it.
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    # Make required Python version compliant with official TF docs (https://www.tensorflow.org/install)
    # It follows: We build a pure Python wheel
    # Note that Python used to build the sources specifies the Python version of the dist (relevant during build only)
    # See https://packaging.python.org/guides/distributing-packages-using-setuptools/#pure-python-wheels for more info
    # We also restrict the code to >=3.6 to fully benefit from type annotations
    # See https://realpython.com/python-type-checking/ for more info
    # No source distribution support for 3.10 yet
    # See https://stackoverflow.com/questions/69458399/numpy-1-21-2-may-not-yet-support-python-3-10
    # See https://github.com/numpy/numpy/issues/17044
    python_requires=">=3.6,<3.10",
    install_requires=requirements,
    extras_require=extra_requirements,
    # List additional URLs that are relevant to your project as a dict.
    # The key is what's used to render the link text on PyPI.
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    project_urls={
        "ZEN Intellesis": "https://www.zeiss.com/microscopy/int/products/microscope-software/zen-intellesis-image-segmentation-by-deep-learning.html"
    },
)
