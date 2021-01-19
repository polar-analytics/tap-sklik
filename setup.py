from distutils.core import setup

setup(
    name="tap-sklik",
    version="0.1.0",
    packages=[
        "tap_sklik",
    ],
    long_description=open("README.md").read(),
    install_requires=[
        "requests>=2.20.0",
        "python-dotenv>=0.15.0",
        "singer-python>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "tap-sklik=tap_sklik.singer.cli:cli",
        ],
    },
)
