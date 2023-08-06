import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gh-downloader",
    version="0.0.1",
    author="antwxne",
    author_email="antoine.desruet@epitech.eu",
    description="CLI to download repos from Github.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antwxne/Github-downloader",
    project_urls={
        "Bug Tracker": "https://github.com/antwxne/Github-downloader/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points={
        'console_scripts': [
            "gh-downloader=main:cli"
        ]
    },
    install_requires=[
        "inquirer",
        "requests",
        "tqdm"
    ]
)
