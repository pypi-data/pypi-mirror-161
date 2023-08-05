from setuptools import setup
from os import environ, path
from shutil import rmtree

package_name = environ.get("PACKAGE_NAME", "").strip()

if not package_name:
    raise RuntimeError("Specify package name as a PACKAGE_NAME env variable!")

dist = path.join(path.dirname(__file__), "dist")
rmtree(dist, ignore_errors=True)

setup(
    name=package_name,
    version="0.0.0",
    description=(
        "This package stands as a placeholder for Ampio packages maintained in private pypi "
        "repositories. The purpose of such action is to prevent supply chain attacks."
    ),
    python_requires=">=99.0",
    author="Michał Getka",
    url="https://ampio.com",
    packages=["placeholder"],
)
