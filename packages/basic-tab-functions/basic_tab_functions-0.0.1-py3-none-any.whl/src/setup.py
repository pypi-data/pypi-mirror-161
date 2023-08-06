import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="basic_tab_functions",
    version="0.0.1",
    author="Hallgrímur Eggertsson",
    author_email="HallgrimurV@gmail.com",
    description="Useful .txt i/o package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/demopackage",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)