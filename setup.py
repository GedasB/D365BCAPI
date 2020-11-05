import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="D365BCAPI-GEDASB", # Replace with your own username
    version="0.0.1b1",
    author="Gedas B",
    author_email="gedasb@outlook.com",
    description="Dynamics 365 Business Central API connector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gedasb/D365BCAPI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    keywords='Microsoft Dynamics 365 Business Central NAV API ',
)