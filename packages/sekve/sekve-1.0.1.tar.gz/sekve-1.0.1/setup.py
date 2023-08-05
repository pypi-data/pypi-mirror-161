# Setup for PyPI 'sekve' compilation
# Needs to be in the \sekv-e folder for compilation
import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="sekve",
    version="1.0.1",

    description="SEKV-E is a Python-based parameters extractor for the simplified EKV model.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://gitlab.com/moscm/sekv-e",
    author="Hung-Chi Han, Vicente Carbon",
    author_email="hung.han@epfl.ch",
    license='MIT',

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="ekv, sekv, extractor, modeling, MOSFET",

    packages=find_packages(include=['sekve','sekve.*']),
    install_requires=[
       "matplotlib==3.5.1",
       "numpy==1.22.3",
       "pandas==1.4.2",
       "scipy==1.7.3",
    ],
    python_requires=">=3.7, <4",
    project_urls={  # Optional
        "Git": "https://gitlab.com/moscm/sekv-e",
    },
)
