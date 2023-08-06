import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fund_alchemy",
    version="1.0.15",
    author="xxf",
    author_email="shoesflying@163.com",
    descroption="A fund analysis platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ShoesFly/fund_alchemy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
