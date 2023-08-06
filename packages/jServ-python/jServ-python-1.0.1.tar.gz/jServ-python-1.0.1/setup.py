import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jServ-python",
    version="1.0.1",
    author="Codealchemi",
    author_email="kris@codealchemi.com",
    description="Python library for interfacing with jServ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Codealchemi/jServ-python-lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',
    ]
)
