import os

from setuptools import setup, find_packages

description = (
    "INCOMPATIBLE FORK OF CURRENT PYCONTRACTS ON GITHUB"
    "The version on pypi is stale, this is a fork that is updated from github and"
    "with added support for jax. No guarantee that this will be kept up to date, or developed further"
    "or kept compatible with the original."
    "See the original repo here: http://andreacensi.github.com/contracts/"
)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


long_description = read("README.rst")


def get_version(filename):
    import ast

    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith("__version__"):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError("No version found in %r." % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename="src/contracts/__init__.py")

setup(
    name="PyContracts-mirror",
    author="xivarri",
    author_email="xamvolagis@gmail.com",
    url="",
    description=description,
    long_description=long_description,
    keywords="type checking, value checking, contracts",
    license="LGPL",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    version=version,
    download_url="",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["pyparsing", "decorator", "six", "future"],
    tests_require=["nose"],
    entry_points={},
)
