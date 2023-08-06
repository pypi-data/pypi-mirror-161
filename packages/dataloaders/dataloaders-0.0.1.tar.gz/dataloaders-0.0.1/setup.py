from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()


if __name__ == "__main__":
    setup(
        name="dataloaders",
        version="0.0.1",
        description="dataloaders",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="Abhishek Thakur",
        url="https://github.com/abhishekkrthakur/dataloaders",
        license="Apache License",
        packages=find_packages(),
        include_package_data=True,
        install_requires=["torch>=1.10.0"],
        platforms=["linux", "unix"],
        python_requires=">=3.8",
    )
