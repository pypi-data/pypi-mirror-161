from setuptools import setup

setup(
    name="teleterm",
    version="0.0.8",
    description="teleterm",
    long_description=open("README.txt").read(),
    long_description_content_type="text/plain",
    url="https://duckduckgo.com",
    author="Ragar Rysuv",
    license="",
    packages=["teleterm"],
    install_requires=[
        "requests",
        "bs4",
    ],
    entry_points={
      "console_scripts": ["teleterm = teleterm.tele:cli"],
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.7",
        "Operating System :: POSIX :: Linux",
    ],
)
