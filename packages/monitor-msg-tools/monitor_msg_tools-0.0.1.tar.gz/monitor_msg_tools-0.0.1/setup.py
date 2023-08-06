import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="monitor_msg_tools",
    version="0.0.1",
    author="vSir",
    author_email="weiguo341@gmail.com",
    description="simple tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nevquit/monitor_msg_tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
    'pandas==0.24.2','requests==2.25.1'
    ]
)