import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='parshu',
    version='1.0.1',
    scripts=['parshu'] ,
    author="Eshan Singh",
    author_email="r0x4r@yahoo.com",
    description="Parshu uses regex to filter out the custom results. Filter URLs to save your time.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/R0X4R/Parshu",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
