import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-jae-han",
    version="0.0.1",
    author="Jae Han",
    author_email="j.sunny.han@gmail.com",
    description="A small API used for querying auto insurance policy data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codebrotherone/ledger.git",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.9',
)