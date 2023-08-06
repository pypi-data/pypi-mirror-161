import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="natural2lean_cli",
    version="0.0.1",
    author="Augustin d'Oultremont",
    author_email="augustin.doultremont@outlook.com",
    description="Command line interface for natural2lean package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Augustindou/natural2lean-cli",
    project_urls={
        "Bug Tracker": "https://github.com/Augustindou/natural2lean-cli/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src", exclude=["*-old"]),
    entry_points={
        "console_scripts": [
            "natural2lean=natural2lean_cli.__main__:main",
        ],
    },
    python_requires=">=3.9",
    install_requires=[
        "natural2lean>=0.0.3",
        "inquirerpy",
    ],
    extras_require={
        "dev": [
            "pytest>=3.6",
            "pyperclip",
        ],
    },
)
