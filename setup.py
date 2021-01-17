import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="strong",
    version="0.2.2",
    author="Jérome Eertmans",
    author_email="jeertmans@icloud.com",
    description="Dynamic type checker for function signatures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeertmans/strong",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.8",
    entry_points="""
        [console_scripts]
        strong=strong.scripts.strong:main
    """,
)
