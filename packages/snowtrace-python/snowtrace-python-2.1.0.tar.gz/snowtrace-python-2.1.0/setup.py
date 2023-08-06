from setuptools import setup

setup(
    name="snowtrace-python",
    version="2.1.0",
    description="A minimal, yet complete, python API for snowtrace.io.",
    url="https://github.com/EmperorMew/snowtrace-python",
    author="snowcone",
    author_email="info@snowcones.io",
    license="MIT",
    packages=[
        "snowtrace",
        "snowtrace.configs",
        "snowtrace.enums",
        "snowtrace.modules",
        "snowtrace.utils",
    ],
    install_requires=["requests"],
    include_package_data=True,
    zip_safe=False,
)
