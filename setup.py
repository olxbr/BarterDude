from setuptools import setup, find_packages

with open("requirements.txt") as reqs:
    requirements = reqs.read().split("\n")

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="barterdude",
    version="DYNAMIC",
    description="Message exchange engine to build pipelines in brokers like RabbitMQ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Olx",
    license='Apache 2',
    url='https://github.com/olxbr/BarterDude/',
    download_url='https://github.com/olxbr/BarterDude/archive/master.zip',
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    packages=find_packages()
)
