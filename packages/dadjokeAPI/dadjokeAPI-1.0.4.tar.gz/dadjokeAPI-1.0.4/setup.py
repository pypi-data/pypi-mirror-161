import setuptools

with open("README.md") as rmd:
    ldesc = rmd.read()

setuptools.setup(
    name="dadjokeAPI",
    version="1.0.4",
    author="Aochi",
    author_email="aochi@fuquila.net",
    description="A simple API wrapper for your dad joke needs.",
    long_description=ldesc,
    long_description_content_type="text/markdown",
    url="https://github.com/7ez/dadjokeAPI",
    install_requires=["aiohttp", "requests"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7"
)