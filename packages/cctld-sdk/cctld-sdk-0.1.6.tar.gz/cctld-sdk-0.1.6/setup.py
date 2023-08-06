from setuptools import find_packages, setup

setup(
    name="cctld-sdk",
    packages=find_packages(exclude=["tests"]),
    version="0.1.6",
    description="CCTLD SDK",
    author="karimov.oqil@gmail.com, mr.arabboy@gmail.com",
    license="MIT",
    install_requires=["dicttoxml", "requests", "xmltodict"],
    setup_requires=["wheel", "pytest-runner"],
    tests_require=["pytest==4.4.1"],
    test_suite="tests",
)
