import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bioimageit_formats",
    version="0.1.1",
    author="Sylvain Prigent",
    author_email="sylvain.prigent@inria.fr",
    description="Manage data formats for BioImageIT project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bioimageit/bioimageit_formats",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "numpy",
        "pandas",
        "scikit-image>=0.18.3",
        "zarr>=2.12.0"
    ],
)
