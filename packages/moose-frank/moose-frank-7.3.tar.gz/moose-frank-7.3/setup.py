#!/usr/bin/env python

from setuptools import find_packages, setup


version = "7.3"

setup(
    name="moose-frank",
    packages=find_packages(),
    version=version,
    description="A Python package packed with tools that are commonly used in "
    "Moose projects.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sven Groot (Mediamoose)",
    author_email="sven@mediamoose.nl",
    url="https://gitlab.com/mediamoose/moose-frank/tree/v{}".format(version),
    download_url="https://gitlab.com/mediamoose/moose-frank/repository/v{}/archive.tar.gz".format(
        version
    ),
    include_package_data=True,
    install_requires=["django>=1.11"],
    extras_require={
        "graphene": [
            "graphene-django>=2.15",
            "graphene-file-upload>=1.3",
            "graphene>=2.1",
        ],
        "gcloud": [
            "django-storages[google]>=1.11",
        ],
    },
    license="MIT",
    zip_safe=False,
    keywords=["moose", "frank", "frankenstein"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
