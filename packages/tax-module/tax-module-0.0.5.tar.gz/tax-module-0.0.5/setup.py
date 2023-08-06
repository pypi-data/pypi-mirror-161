from setuptools import setup, find_packages

setup(
    name="tax-module",
    version="0.0.5",
    description="Tax module",
    url="https://github.com/Shuttl-Tech/tax-module.git",
    author="Shuttl",
    author_email="sherub.thakur@shuttl.com",
    license="MIT",
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3.7"],
    install_requires=["pytz", "voluptuous", "pyshuttlis"],
    extras_require={
        "test": ["pytest", "pytest-runner", "pytest-cov", "pytest-pep8"],
        "dev": ["flake8"],
    },
)
