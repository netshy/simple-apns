import os
from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read the version from simple_apns/__init__.py
with open(os.path.join("simple_apns", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break
    else:
        version = "0.1.0"

setup(
    name="simple-apns",
    version=version,
    description="Synchronous Python client for Apple Push Notification Service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ivan Lundak",
    author_email="n3tshy@gmail.com",
    url="https://github.com/netshy/simple-apns",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "httpx[http2]>=0.20.0",
        "PyJWT>=2.0.0",
        "cryptography>=3.4.0",
    ],
    extras_require={
        "django": ["Django>=2.2"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2",
            "mypy>=0.901",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
    ],
    keywords="apns,push,notifications,apple,ios,django",
)