from setuptools import setup, find_packages

VERSION = '0.0.3'
DESCRIPTION = 'My first Python package'
LONG_DESCRIPTION = 'My first Python package'

# Setting up
setup(
    # the name must match the folder name 'armanfirstpackage'
    name="armanfirstpackage",
    version=VERSION,
    author="Md. Arman Hossain",
    author_email="shanto377@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'first package'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
