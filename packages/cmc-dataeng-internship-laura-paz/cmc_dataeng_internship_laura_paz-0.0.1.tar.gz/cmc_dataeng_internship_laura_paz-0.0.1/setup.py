import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cmc_dataeng_internship_laura_paz",
    version="0.0.1",
    author="Laura Paz",
    description="Exercise 13",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[]
)
