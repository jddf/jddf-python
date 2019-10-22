import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jddf",
    version="0.1.1",
    author="Ulysse Carion",
    author_email="ulysse@segment.com",
    description="JSON Data Definition Format support for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jddf/jddf-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'strict_rfc3339==0.7'
    ]
)
