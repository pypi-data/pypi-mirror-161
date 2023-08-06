import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tdautils",
    version="1.1.7",
    author="DrEdwC",
    author_email="ed@topfintech.org",
    description="A trade date generator for quant model of Chinese stock market",
    long_description="This package includes a collection of tools for  offseting, generating trade date series used in quant analysis. Based on a pre-saved Chinese stock market calendar (since year 1991), this package enables user to quickly find trade date(e,g the most recent trade date, a offset trade date from an anchor date) or generate a user-specified datetime index for back-testing or quant modeling",
    long_description_content_type="text/markdown",
    url="https://github.com/edwincca/stockpriceanna/blob/master/README.md",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)