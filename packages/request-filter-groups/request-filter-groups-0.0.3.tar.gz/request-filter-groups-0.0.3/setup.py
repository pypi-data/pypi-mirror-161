from setuptools import setup
from pathlib import Path

setup(
    name="request-filter-groups",
    version="0.0.3",
    description="Uses filter groups to validate requests",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/marshall7m/request-filter-groups",
    author="Marshall Mamiya",
    license="Apache 2.0",
    packages=["request_filter_groups"],
    install_requires=["flask", "validator==0.7.1", "jsonpath-ng==1.5.3"],
    extras_require={"tests": ["pytest"]},
    classifiers=[
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
