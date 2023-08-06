import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wikimedia_connection",
    version="0.0.1",
    author="Mateusz Konieczny",
    author_email="matkoniecz@gmail.com",
    description="Not recommended for an actual use, nowadays I would write something far better.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://codeberg.org/matkoniecz/wikimedia_connection",
    packages=setuptools.find_packages(),
    install_requires = [
        'urllib3>=1.13.1',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
