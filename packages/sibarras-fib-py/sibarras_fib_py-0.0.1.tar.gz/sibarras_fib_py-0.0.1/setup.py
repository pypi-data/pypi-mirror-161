from setuptools import find_packages, setup

with open("README.md", 'r') as fh:
    long_description = fh.read()

setup(
    name="sibarras_fib_py",
    version="0.0.1",
    author="Samuel Ibarra",
    author_email="ing.samuelibarra@gmail.com",
    description="Calculates a fibonacci number",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sibarras/sibarras-fib-py.git",
    install_requires=[],
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