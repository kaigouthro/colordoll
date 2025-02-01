import setuptools
import json

# Load long description from README.md
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="colordoll",
    version='0.1.0', 
    author="kai gouthro",
    author_email="",
    description="Colorize text and data structures in the terminal with ANSI escape codes and themed decorators.",
    long_description=long_description, 
    long_description_content_type="text/markdown",
    url="https://github.com/kaigouthro/colordoll",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires=">=3.6",
)