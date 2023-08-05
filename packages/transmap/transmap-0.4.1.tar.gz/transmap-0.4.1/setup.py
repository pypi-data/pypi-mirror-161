from os import getenv
from setuptools import find_namespace_packages, setup
from glob import glob

requirement_files = glob("**/requirements.txt", recursive=True)

REQUIREMENTS = []

for requirement_file in requirement_files:
    with open(requirement_file, "r") as file:
        REQUIREMENTS.extend([line.rstrip() for line in file.readlines()])

setup(
    name="transmap",
    packages=find_namespace_packages(
        include=['transmap', 'transmap.*'],
        exclude=['*tests*']
    ),
    version=f"{getenv('CI_COMMIT_TAG', '0.4.1')}",
    description="API for Transmap Hub",
    author="Christopher C Angel, PhD",
    license="MIT",
    install_requires=list(set(REQUIREMENTS))
)
