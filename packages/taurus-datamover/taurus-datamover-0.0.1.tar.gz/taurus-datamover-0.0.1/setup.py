import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="taurus-datamover",
    version="0.0.1",
    author="Till Korten",
    author_email="till.korten@tu-dresden.de",
    description="Python wrapper for the datamover tools that enable moving data between the ZIH fileserver and the taurus cluster at TU Dresden",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.mn.tu-dresden.de/bia-pol/taurus-datamover/",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
    ],
)
