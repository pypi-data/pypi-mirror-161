from setuptools import setup, find_packages
from pathlib import Path

root = Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (root / "README.rst").read_text(encoding="utf-8")

setup(
    name="django-ref",
    version="0.5.2",
    description="A Django app defining data models for managing "
    "bibliographic references for scientific databases.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/xnx/django-valem",
    author="Christian Hill, Frances Skinner, Iouli Gordon, Robert Hargreaves,"
    " Kelly Lockhart",
    author_email="ch.hill@iaea.org",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Django",
        "Operating System :: OS Independent",
    ],
    keywords="django, database, references, citation",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "Django>=3.2",
        "requests>=2.28.1",
    ],
    extras_require={"dev": ["black", "coverage", "ipython"]},
    project_urls={
        "Bug Reports": "https://github.com/xnx/django-pyref/issues",
    },
)
