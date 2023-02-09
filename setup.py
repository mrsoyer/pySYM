import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scrapyomama",
    version="0.0.3",
    author="Thomas Garcia",
    author_email="garciathomas@gmail.com",
    description="Scrap Yo Mama",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrsoyer/symtest",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)