from setuptools import find_packages, setup
from pathlib import Path

with open("README.md", 'r') as rme:
    long_description = rme.read()

with open("./sibarras_fib_py/version.py", 'rt') as vr:
    version = vr.read().split("=")[1].replace("'", "")

setup(
    name="sibarras_fib_py",
    version=version,
    author="Samuel Ibarra",
    author_email="ing.samuelibarra@gmail.com",
    description="Calculates a fibonacci number",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sibarras/sibarras-fib-py.git",
    install_requires=[
        "PyYAML>=4.1.2",
        "dill>=0.2.8"
    ],
    extras_require={
        'server': ["Flask>=1.0.0"]
    },
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    test_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fib-number = sibarras_fib_py.cmd.fib_numb:fib_numb', 
        ]
    }
)