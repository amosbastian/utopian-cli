from setuptools import setup, find_packages

requirements = ["Click", "requests", "python-dateutil"]

setup(
    name="utopian",
    version="0.2.0",
    description="A CLI for the Utopian.io API.",
    license="MIT",
    author="amosbastian",
    author_email="amosbastian@gmail.com",
    packages=find_packages(),
    install_requires=requirements,
    entry_points="""
        [console_scripts]
        utopian=utopian.utopian:cli
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6"
    ],
    keywords="utopian cli"
)