import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iWAN",
    version="0.0.2",
    author="vSir",
    author_email="weiguo341@gmail.com",
    description="simple tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nevquit/iWAN",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
    'websocket-client==0.58.0'
    ]
)