from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = []

setup(
    name="LibBinTViewVariable",
    version="0.1.4.7.4",
    author="Yonas Guryavichyus",
    author_email="yagur1998@gmail.com",
    description="A package to share constants from Binance and TradingView",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Vankezzz/BinTViewVariable/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)