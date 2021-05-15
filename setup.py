import os

import setuptools


def get_version():
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, "kokex", "__init__.py")) as f:
        for line in f.read().splitlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")


def get_description():
    with open("README.md", "r") as f:
        return f.read()


setuptools.setup(
    name="kokex",
    version=get_version(),
    author="jsmyung",
    author_email="jsmyung@datansoft.com",
    description="A Korean Keywords Extractor with Syntactic Analysis",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/jsmyung-datansoft/kokex",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "konlpy>=0.5.2",
        "networkx>=2.5.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
