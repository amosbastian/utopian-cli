from setuptools import setup

setup(
    name="utopian",
    version="0.1.0",
    py_modules=["utopian"],
    install_requires=[
        "Click",
        "requests"
    ],
    entry_points="""
        [console_scripts]
        utopian=utopian:cli
    """,
)