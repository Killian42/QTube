from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="QTube",
    version="2.4.0",
    description="Automatically add Youtube videos to a playlist.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Killian Lebreton",
    author_email="killian.lebreton35@gmail.com",
    url="https://github.com/Killian42/QTube",
    project_urls={"Source": "https://github.com/Killian42/QTube"},
    entry_points={
        "console_scripts": [
            "qtube = QTube.scripts.qtube:main",
        ]
    },
    packages=find_packages(exclude=("QTube.tests",)),
)
