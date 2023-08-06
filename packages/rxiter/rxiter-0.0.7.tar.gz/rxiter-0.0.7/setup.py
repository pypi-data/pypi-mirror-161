from setuptools import setup

with open("README.md") as fp:
    long_description = fp.read()

setup(
    name="rxiter",
    license="MIT",
    version="0.0.7",
    packages=["rxiter"],
    long_description=long_description,
    long_description_content_type='text/markdown',
    description="Observable operations for async generators",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python"
    ]
)
