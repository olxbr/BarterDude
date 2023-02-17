from setuptools import setup, find_packages

libs = []  # if need extra libs

extra = {
    "all": [],

}

with open("requirements/requirements_base.txt") as reqs:
    raw_requirements = reqs.read().split("\n")

requirements = []
for r in raw_requirements:
    if r.startswith("git+"):
        name = r.split(".git@")[0].split("/")[-1]
        requirements.append(f"{name} @ {r}")
    else:
        requirements.append(r)

for lib in libs:
    with open(f"requirements/requirements_{lib}.txt") as reqs:
        extra[lib] = reqs.read().split("\n")
        extra["all"] = extra["all"] + extra[lib]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="barterdude",
    description="Message exchange engine to build pipelines using brokers like RabbitMQ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Olx",
    license='Apache 2',
    include_package_data=True,
    url='https://github.com/olxbr/BarterDude/',
    download_url='https://github.com/olxbr/BarterDude/archive/master.zip',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=requirements,
    extras_require=extra,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    packages=find_packages()
)
