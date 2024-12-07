from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="plexsearch",
    version="0.1.0",
    author="Tom Doerr",
    author_email="",  # Add your email if you want
    description="A powerful Python tool for performing technical searches using the Perplexity API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tom-doerr/perplexity_search",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "plexsearch=plexsearch.core:main",
        ],
    },
)
