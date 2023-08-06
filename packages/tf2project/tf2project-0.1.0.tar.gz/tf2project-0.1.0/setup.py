# Terraform Test Framework
# https://github.com/tf2project/tf2project

from os import environ

from setuptools import find_packages, setup

from tf2 import __version__

if environ.get("ENV", "production") == "development":
    with open("requirements.txt") as f:
        requirements = f.readlines()
else:
    requirements = []

with open("README.md") as f:
    readme = f.read()

setup(
    name="tf2project",
    description="Terraform Test Framework",
    author="Saeid Bostandoust",
    author_email="ssbostan@yahoo.com",
    license="Apache License 2.0",
    url="https://github.com/tf2project/tf2project",
    long_description=readme,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://tf2project.io",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Security",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Testing",
    ],
    version=__version__,
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=False,
    zip_safe=True,
)
