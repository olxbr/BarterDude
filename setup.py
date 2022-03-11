import os
from setuptools import setup, find_packages

libs = []  # if need extra libs

extra = {
    "all": [],

}

with open("requirements/requirements_base.txt") as reqs:
    requirements = reqs.read().split("\n")

for lib in libs:
    with open(f"requirements/requirements_{lib}.txt") as reqs:
        extra[lib] = reqs.read().split("\n")
        extra["all"] = extra["all"] + extra[lib]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="barterdude",
    version=os.getenv('RELEASE_VERSION') if os.getenv('RELEASE_VERSION') else os.getenv('1.0.1', 'DYNAMIC'),
    description="Message exchange engine to build pipelines using brokers like RabbitMQ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Olx",
    license='Apache 2',
    include_package_data=True,
    url='https://github.com/olxbr/BarterDude/',
    download_url='https://github.com/olxbr/BarterDude/archive/master.zip',
    install_requires=requirements,
    extras_require=extra,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    packages=find_packages()
)
