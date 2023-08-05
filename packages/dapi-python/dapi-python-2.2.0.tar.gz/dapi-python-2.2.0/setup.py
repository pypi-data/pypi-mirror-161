import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

url = "https://github.com/dapi-co/dapi-python"

setuptools.setup(
    name="dapi-python",
    version='2.2.0',
    author="DAPI LTD",
    author_email="dev@dapi.com",
    description="Python Library for Dapi API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests>=2.7.0'],
    python_requires='>=3.6',
)
