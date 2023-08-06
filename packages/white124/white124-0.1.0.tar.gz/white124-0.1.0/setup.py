import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="white124",
    version="0.1.0",
    author="Alexander White",
    author_email="pip@mail83.ru",
    description="Combining methods for convenience in new projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/white124bk/",
    packages=setuptools.find_packages(),
    install_requires=[
        'pymysql'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)