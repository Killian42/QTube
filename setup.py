from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="QTube",
    version="2.0.0",
    description="Automatically add Youtube videos to a playlist.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    py_modules=["library", "run"],
    package_dir={"": "QTube"},
    author="Killian Lebreton",
    author_email="killian.lebreton35@gmail.com",
    url="https://github.com/Killian42/QTube",
)
