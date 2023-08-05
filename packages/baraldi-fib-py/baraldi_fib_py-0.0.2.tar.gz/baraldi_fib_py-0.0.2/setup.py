import pathlib
from setuptools import find_packages, setup

with open(str(pathlib.Path(__file__).parent.absolute()) + "/baraldi_fib_py/version.py", "r", encoding="utf-8") as fh:
    version = fh.read().split("=")[1].replace("'", "")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="baraldi_fib_py",
    version=version,
    author="Enzo Baraldi",
    description="Calculates a Fibonacci number",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Enzo1603/baraldi-fib-py.git",
    install_requires=[],
    packages=find_packages(exclude=("tests",)),
    entry_points={
        "console_scripts": [
            "fib-number = baraldi_fib_py.cmd.fib_num:fib_num",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3",
    tests_require=["pytest"],
)
