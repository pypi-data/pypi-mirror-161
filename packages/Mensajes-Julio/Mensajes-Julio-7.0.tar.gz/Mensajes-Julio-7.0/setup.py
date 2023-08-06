from setuptools import setup, find_packages

setup(
    name="Mensajes-Julio",
    version="7.0",
    description="Un paquete para saludar y despedir",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author= "Julio PERU",
    author_email="misarirosalesj@gmail.com",
    url="http://hcosta.info",
    license_files=["LICENSE"],
    packages=find_packages(),
    scripts=[],
    test_suite="tests",
    install_requires=[paquete.strip() for paquete in open("requirements.txt").readlines()],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
)