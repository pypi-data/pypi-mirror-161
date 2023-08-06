import os

from setuptools import find_packages, setup

version_contents = {}
version_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "version.py"
)
with open(version_path, "rt") as f:
    exec(f.read(), version_contents)

setup(
    name="wenxin-api",
    description="wenxin-api client for wenxin 1p5b 10b 100b prompt tuning and serving",
    version=version_contents["VERSION"],
    install_requires=[
        "requests>=2.20",
        "tqdm"
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "": ["*.so"]
    },
    author="xuchenning",
)