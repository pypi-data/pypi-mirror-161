import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(
    name="radiant-rdkit",
    version="0.2.0",
    author="Julian M. Kleber",
    author_email="julian.kleber@sail.black",
    description="short package to make publication quality rdkit plots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://codeberg.org/sail.black/acheeve.git",
    packages=setuptools.find_packages(include=["radiant*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'rdkit',
          'cairosvg'
      ],
    python_requires=">=3.9",
)
