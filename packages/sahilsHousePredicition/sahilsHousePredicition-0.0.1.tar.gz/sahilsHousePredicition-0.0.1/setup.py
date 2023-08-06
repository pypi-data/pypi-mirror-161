from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

setup(
    name="sahilsHousePredicition",
    version="0.0.1",
    description="House Predicition Notebook",
    long_description=open("README.txt").read() + "\n\n" + open("CHANGELOG.txt").read(),
    url="",
    author="Sahil Jaswal",
    author_email="sj89808@gmail.com",
    license="MIT",
    classifiers=classifiers,
    keywords="prediction",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "mlflow[extra]",
        "jupyter",
        "pipfile",
        "tensorflow",
        "keras",
    ],
)
