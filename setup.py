from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="Youtube_Bot",
    version="0.0.1",
    description="Add youtube videos to a playlist automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    py_modules=["library", "run"],
    package_dir={"": "src"},
    author="Killian Lebreton",
    author_email="killian.lebreton35@gmail.com",
    url="https://github.com/Killian42/Youtube-Bot",
)
