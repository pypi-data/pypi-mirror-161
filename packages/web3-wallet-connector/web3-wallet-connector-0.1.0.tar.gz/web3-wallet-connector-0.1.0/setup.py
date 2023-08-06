from setuptools import setup

try:
    import sys

    from semantic_release import setup_hook

    setup_hook(sys.argv)
except ImportError:
    pass

__version__ = "0.1.0"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="web3-wallet-connector",
    version=__version__,
    author="Aliaksandr Burakou",
    author_email="alex.burakou@gmail.com",
    description=(
        "Python library that facilitates interaction with ethereum wallet address."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SinxRofozoteron/web3-token-connector",
    license="MIT",
    packages=["web3-wallet-connector"],
    install_requires=["web3==6.0.0b4"],
)
