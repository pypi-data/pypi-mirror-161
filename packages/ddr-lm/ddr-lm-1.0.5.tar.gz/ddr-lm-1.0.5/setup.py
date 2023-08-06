import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ddr-lm", # DDR LM integration package
    version="1.0.5", #Update the version number here
    author="Peter Van Horne",
    author_email="petervh@cisco.com",
    description="Distributed Device Reasoning (DDR) and Lazy Maestro integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://wwwin-github.cisco.com/petervh/ddr-lm",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
                     ],
    python_requires='>=3.9',
    py_modules=['mlmddr', 'lmautomation'],
    )
