import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="configchain",  # Replace with your own username
    version="0.3.12",
    author="Luo Tao",
    author_email="lotreal@gmail.com",
    description="hierarchical configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lotreal/configchain",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
