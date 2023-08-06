# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

p_version = "0.0.1"

req = ["bleach==5.0.1",
       "certifi==2022.6.15",
       "charset-normalizer==2.1.0",
       "commonmark==0.9.1",
       "docutils==0.19",
       "idna==3.3",
       "importlib-metadata==4.12.0",
       "keyring==23.7.0",
       "pkginfo==1.8.3",
       "Pygments==2.12.0",
       "pywin32-ctypes==0.2.0",
       "readme-renderer==35.0",
       "requests==2.28.1",
       "requests-toolbelt==0.9.1",
       "rfc3986==2.0.0",
       "rich==12.5.1",
       "six==1.16.0",
       "twine==4.0.1",
       "urllib3==1.26.11",
       "webencodings==0.5.1",
       "zipp==3.8.1"]

print(req)

with open("README.md") as f:
    long_description = f.read()

setup(
    name="AEngineConsole",
    version=p_version,
    author="Alex Abdelnur",
    author_email="a.aabdelnur@mail.ru",
    packages=find_packages(),
    url="https://github.com/aaalllexxx/AEngine_console",
    download_url="https://github.com/aaalllexxx/AEngine_console",
    description="Console applications engine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "console",
        "terminal",
        "engine"
    ],
    install_requires=req
)
