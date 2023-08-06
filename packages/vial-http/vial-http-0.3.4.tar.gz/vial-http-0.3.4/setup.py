import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "vial-http",
    version = "0.3.4",
    author = "Martin Wacker",
    author_email = "martas@imm.cz",
    description = "WSGI based HTTP nano-framework",
    license = "MIT",
    keywords = "http server minimal wsgi api",
    url = "https://github.com/martastain/vial",
    packages=['vial'],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server"
    ],
)
