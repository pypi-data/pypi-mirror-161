import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bpp_env_helpers",
    version="0.0.8",
    author="matthew bahloul",
    author_email="matthew.bahloul@blueprintprep.com",
    description="misc helpers for bpp behave tests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/blueprintprep/bpp-qa/utilities/environment-helpers",
    project_urls={
        "Bug Tracker": "https://gitlab.com/blueprintprep/bpp-qa/utilities/environment-helpers/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(exclude=('tests',)),
    python_requires=">=3.6",
)
