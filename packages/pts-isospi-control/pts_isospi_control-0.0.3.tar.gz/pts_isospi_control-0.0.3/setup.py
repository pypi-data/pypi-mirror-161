from setuptools import find_packages, setup
import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pts_isospi_control",
    version="0.0.3",
    description="Controls the PTS ISO SPI Interface",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/pass-testing-solutions/pts-isospi-interface-control",
    author="Pass Testing Solutions GmbH",
    author_email="info@pass-testing.de",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(include=['pts_isospi_control']),
    include_package_data=True,
    install_requires=['python-can','cantools','tabulate'],
)
