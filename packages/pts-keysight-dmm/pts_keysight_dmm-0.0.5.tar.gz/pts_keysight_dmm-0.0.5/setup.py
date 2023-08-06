from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pts_keysight_dmm",
    version="0.0.5",
    author="Pass testing Solutions GmbH",
    description="Keysight DMM 34465A Diagnostic Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="shuparna@pass-testing.de",
    url="https://gitlab.com/pass-testing-solutions/keysight34465a-interface",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    py_modules=["pts_keysight_dmm"],
    install_requires=["RsInstrument~=1.24.0.83", "pyvisa", "pyvisa-py", "aioredis~=1.3.1"],
    packages=find_packages(include=['pts_keysight_dmm']),
    include_package_data=True,
)
