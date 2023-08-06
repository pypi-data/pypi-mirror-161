from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="terrorform",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pytest"],
    license="MIT",
    url="https://github.com/bengetch/terrorform",
    author="bengetch",
    author_email="bengetch@gmail.com",
    description="Terraform wrapper for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.5"
)