from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="memra-sdk",
    version="0.1.0",
    author="Memra",
    author_email="support@memra.com",
    description="Declarative framework for enterprise workflows - Client SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/memra/memra-sdk",
    packages=find_packages(include=['memra', 'memra.*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=1.8.0",
        "httpx>=0.24.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "memra=memra.cli:main",
        ],
    },
) 