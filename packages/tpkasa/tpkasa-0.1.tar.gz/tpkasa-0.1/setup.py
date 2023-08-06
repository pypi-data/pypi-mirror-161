import setuptools


setuptools.setup(
    name="tpkasa",
    version="0.1",
    author="Francis B. Lavoie",
    author_email="francis.b.lavoie@usherbrooke.ca",
    description="python-kasa wrapper",
    long_description="python-kasa wrapper",
    long_description_content_type="text/markdown",
    url="https://catalyseur.ca",
    packages=setuptools.find_packages(),
    install_requires = ["python-kasa"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)