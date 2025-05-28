#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="docx-rtm-automation",
    version="1.0.0",
    description="Requirements Traceability Matrix (RTM) Automation Tool",
    author="RTM Team",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "pyyaml",
        "docx2python",
        "markdown",
        "rich",
        "lxml",
    ],
    extras_require={
        "dev": [
            "flake8",
            "black",
            "isort",
            "mypy",
            "pytest-cov",
            "pylint",
            "ruff",
        ]
    },
    python_requires=">=3.9",
)
