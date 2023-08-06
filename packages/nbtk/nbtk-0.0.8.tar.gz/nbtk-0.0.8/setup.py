import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nbtk",
    version="0.0.8",
    author="@Nebula Team",
    author_email="wzl@zhejianglab.com",
    description="Nebula Toolkit, serving developers and contributors of the Nebula platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.zjvis.org/bigdata/aiworks-py/tree/dev/nbtk",
    # project_urls={
    #     "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)