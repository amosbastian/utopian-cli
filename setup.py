from setuptools import setup, find_packages

requirements = ["Click", "requests"]

setup(
    name="utopian",
    version="0.1.0",
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
        "Intended Audience :: Utopian.io Users",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="utopian cli"
)