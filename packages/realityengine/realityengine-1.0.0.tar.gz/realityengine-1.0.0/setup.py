from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS"
]

setup(
    name="realityengine",
    version="1.0.0",
    description="realityengine is a game library designed to make game development with Python easy.",
    long_description=open("README.txt").read() + "\n\n" + open("CHANGELOG.txt").read(),
    long_description_content_type="text/x-rst",
    url="",
    author="Nathaniel Chandler",
    author_email="nchand05@outlook.com",
    license="MIT",
    classifiers=classifiers,
    keywords="Python, Game Development, Educational",
    packages=find_packages(),
    install_requires=['simpleaudio', 'playsound']
)