import setuptools

setuptools.setup(
    name='BrawlhallaPy',
    version='1.0',
    package_dir={'': "BrawlhallaPy"},
    packages=setuptools.find_packages(where="src"),
    license="GNU General Public License v3.0",
    author='HexyeDEV',
    author_email='dragonsale22@gmail.com',
    url='https://github.com/HexyeDEV/Brawlhalla.py',
    description="A python package to get brawlhalla players ranks",
    long_description=open("./README.rst", "r").read(),
        classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
        python_requires=">=3.6",
    )