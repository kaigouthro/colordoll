import setuptools
import json

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="colordoll",
    version='0.1.4',
    author="kai gouthro",
    author_email="",
    description="Colorize text and data structures in the terminal with ANSI escape codes and themed decorators.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kaigouthro/colordoll",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyYAML",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
