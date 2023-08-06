"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express 
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fenlmagic",
    version="0.0.17",
    author="Kaskada",
    author_email="support@kaskada.com",
    description="An IPython extension for executing Fenl",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://kaskada.com",
    project_urls={
        "Documentation": "https://docs.kaskada.com",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Jupyter",
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
    ],
    package_dir={"": "src"},
    packages=["fenlmagic"],
    python_requires=">=3.6",
    install_requires=[
        'kaskada==0.0.20',
        'kaskada_grpc'
    ],
)
