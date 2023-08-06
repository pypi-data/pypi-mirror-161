import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("VERSION.txt", "r", encoding="utf-8") as fh:
    version = fh.read().strip()

setuptools.setup(
    name="smarterai",
    version=version,
    author="Nevine Soliman and Carlos Medina",
    author_email="dev@smarter.ai",
    description="smarter.ai Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.smarter.ai/",
    license_files=('LICENSE.txt',),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    packages=setuptools.find_packages(where="smarterai"),
    data_files=["VERSION.txt"],
    python_requires=">=3"
)
