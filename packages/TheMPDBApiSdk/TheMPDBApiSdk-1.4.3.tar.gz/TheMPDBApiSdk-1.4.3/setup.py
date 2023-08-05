from setuptools import setup

setup(
    name="TheMPDBApiSdk",
    version="1.4.3",
    packages=['mpdbapi'],
    package_dir={"mpdbapi": "mpdbapi"},
    url="https://thempdb.org",
    license="MIT",
    author="TheMPDB",
    author_email="mandiracieyuphan@gmail.com",
    description="An easy sdk for using https://api.thempdb.org",
    install_requires=["requests"]
)